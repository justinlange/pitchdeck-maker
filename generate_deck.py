#!/usr/bin/env python3
"""Generate visual slide deck images from a markdown deck file using Gemini."""

import argparse
import concurrent.futures
import json
import mimetypes
import os
import sys
import threading
import time

from google import genai
from google.genai import types
from pptx import Presentation
from pptx.util import Emu


PARTITION_MODEL = "gemini-2.5-flash-lite"
IMAGE_MODEL = "gemini-3.1-flash-image-preview"

# Pricing per million tokens (USD) — update as needed
PRICING = {
    PARTITION_MODEL: {"input": 0.075, "output": 0.30, "thinking": 0.30},
    IMAGE_MODEL: {"input": 0.10, "output": 0.40, "thinking": 0.40, "image_output": 3.90},
}


def compute_cost(model, usage):
    """Compute USD cost from usage metadata and model pricing."""
    if usage is None:
        return 0.0, {}
    rates = PRICING.get(model, {})
    breakdown = {}

    prompt_tokens = getattr(usage, "prompt_token_count", 0) or 0
    candidates_tokens = getattr(usage, "candidates_token_count", 0) or 0
    thoughts_tokens = getattr(usage, "thoughts_token_count", 0) or 0

    # Check for image output tokens in modality details
    image_output_tokens = 0
    text_output_tokens = candidates_tokens
    details = getattr(usage, "candidates_tokens_details", None)
    if details:
        for d in details:
            if d.modality and d.modality.name == "IMAGE":
                image_output_tokens = d.token_count or 0
            elif d.modality and d.modality.name == "TEXT":
                text_output_tokens = d.token_count or 0

    input_cost = prompt_tokens / 1_000_000 * rates.get("input", 0)
    output_cost = text_output_tokens / 1_000_000 * rates.get("output", 0)
    thinking_cost = thoughts_tokens / 1_000_000 * rates.get("thinking", 0)
    image_cost = image_output_tokens / 1_000_000 * rates.get("image_output", 0)

    total = input_cost + output_cost + thinking_cost + image_cost
    breakdown = {
        "input_tokens": prompt_tokens,
        "output_tokens": text_output_tokens,
        "thinking_tokens": thoughts_tokens,
        "image_output_tokens": image_output_tokens,
        "input_cost": input_cost,
        "output_cost": output_cost,
        "thinking_cost": thinking_cost,
        "image_cost": image_cost,
        "total": total,
    }
    return total, breakdown

PARTITION_PROMPT = """\
You are a slide deck parser. Given a markdown pitch deck, extract individual slide image generation prompts.

The deck has a global style directive in the first section (before the first ---), \
typically in a blockquote like: > *[SLIDE FORMAT: ...]*

Each slide is separated by --- and may contain a VISUAL blockquote with image generation instructions, \
like: > *[VISUAL — ...]*

For each slide that has a VISUAL directive:
1. Combine the global style directive with the slide-specific VISUAL content into a single, \
complete image generation prompt.
2. The combined prompt should start with the global style parameters (format, background, \
illustration style) then include the full VISUAL description.
3. Remove the blockquote markers (> *[...]*) and clean up the formatting so the result is a \
plain text prompt ready for an image generation model.

Return a JSON array of objects with these fields:
- slide_number (int): 1-indexed position in the deck (counting all slides, including those without visuals)
- title (string): the slide heading text
- prompt (string): the complete image generation prompt
- speaker_notes (string or null): the text after "**SPEAKING NOTES:**" on the slide, if present. \
Include the full text of the speaking notes, cleaned up (no markdown bold markers). Null if no speaking notes.

Only include slides that have a VISUAL directive. Skip slides without one.

Return ONLY valid JSON, no markdown fences or extra text.

Here is the markdown deck:

"""

# Lock for thread-safe printing
_print_lock = threading.Lock()


def log(msg, prefix="INFO"):
    """Thread-safe timestamped log."""
    ts = time.strftime("%H:%M:%S")
    with _print_lock:
        print(f"[{ts}] [{prefix}] {msg}", flush=True)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate slide deck images from a markdown file using Gemini.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
examples:
  %(prog)s deck.md --all                        Generate all slides at 512px
  %(prog)s deck.md --all -r 2k -o ./slides      Generate all at 2K into ./slides
  %(prog)s deck.md --slides 3,5,6,10            Regenerate only slides 3, 5, 6, 10
  %(prog)s deck.md --slides 3+                  Generate slide 3 and all after it
  %(prog)s deck.md --slides 1,2 -r 4k -p 10    Slides 1 & 2 at 4K, 10 workers

environment:
  GEMINI_API_KEY    Required. Your Google Gemini API key.
                    Get one at https://aistudio.google.com/apikey
""",
    )
    parser.add_argument("deck_file", help="Path to the markdown deck file")
    parser.add_argument(
        "-o", "--output", default="./output", help="Output directory (default: ./output)"
    )
    parser.add_argument(
        "-r",
        "--resolution",
        choices=["512", "1k", "2k", "4k"],
        default="512",
        help="Image resolution (default: 512)",
    )
    parser.add_argument(
        "-p",
        "--max-parallel",
        type=int,
        default=20,
        help="Max concurrent image generations (default: 20)",
    )

    # Slide selection: must specify --all or --slides
    slide_group = parser.add_mutually_exclusive_group(required=True)
    slide_group.add_argument(
        "--all",
        action="store_true",
        help="Generate all slides",
    )
    slide_group.add_argument(
        "--slides",
        type=str,
        help="Comma-separated slide numbers (e.g. 3,5,6,10) or N+ for slide N onward (e.g. 3+)",
    )

    return parser.parse_args()


def parse_slide_numbers(slides_str, total_slides=None):
    """Parse '3,5,6,10' or '3+' into a set of ints.

    The '3+' syntax means slide 3 and all slides after it.
    When total_slides is None (before parsing), '3+' stores a
    (start,) tuple as a sentinel; resolve_slide_range() expands it later.
    """
    # Handle the N+ range syntax
    range_match = slides_str.strip()
    if range_match.endswith("+"):
        start_str = range_match[:-1].strip()
        try:
            start = int(start_str)
        except ValueError:
            print(f"Error: invalid slide range '{slides_str}'", file=sys.stderr)
            sys.exit(1)
        if total_slides is not None:
            return set(range(start, total_slides + 1))
        # Return sentinel so main() can expand after parsing
        return {("range_start", start)}

    nums = set()
    for part in slides_str.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            nums.add(int(part))
        except ValueError:
            print(f"Error: invalid slide number '{part}'", file=sys.stderr)
            sys.exit(1)
    return nums


def resolve_slide_range(selected_slides, max_slide_number):
    """Expand range sentinels from parse_slide_numbers into real slide numbers."""
    resolved = set()
    for item in selected_slides:
        if isinstance(item, tuple) and item[0] == "range_start":
            start = item[1]
            resolved.update(range(start, max_slide_number + 1))
        else:
            resolved.add(item)
    return resolved


def partition_deck(client, markdown_content):
    """Use Gemini Flash Lite to parse the deck into individual slide prompts."""
    prompt_text = PARTITION_PROMPT + markdown_content
    log(f"Sending {len(prompt_text):,} chars to {PARTITION_MODEL} for parsing...", "PARSE")

    t0 = time.time()

    # Stream the partition response so we can show progress
    chunks_received = 0
    json_text = ""

    usage = None
    for chunk in client.models.generate_content_stream(
        model=PARTITION_MODEL,
        contents=[
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt_text)],
            ),
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1,
            max_output_tokens=65536,
        ),
    ):
        chunks_received += 1
        if chunk.text:
            json_text += chunk.text
            log(
                f"Chunk {chunks_received}: +{len(chunk.text):,} chars "
                f"(total: {len(json_text):,} chars, "
                f"elapsed: {time.time() - t0:.1f}s)",
                "PARSE",
            )
        if getattr(chunk, "usage_metadata", None):
            usage = chunk.usage_metadata

    elapsed = time.time() - t0
    parse_cost, parse_breakdown = compute_cost(PARTITION_MODEL, usage)
    log(
        f"Partition complete: {len(json_text):,} chars in {elapsed:.1f}s "
        f"({chunks_received} chunks) — cost: ${parse_cost:.4f}",
        "PARSE",
    )

    slides = json.loads(json_text)
    # Validate structure
    for slide in slides:
        if not all(k in slide for k in ("slide_number", "title", "prompt")):
            raise ValueError(f"Invalid slide entry missing required fields: {slide}")

    for s in slides:
        log(f"  Slide {s['slide_number']:2d}: {s['title']} ({len(s['prompt']):,} char prompt)", "PARSE")

    return slides, parse_cost


def save_binary_file(file_name, data):
    with open(file_name, "wb") as f:
        f.write(data)


def generate_slide_image(client, slide, resolution, output_dir):
    """Generate a single slide image using the Gemini image model."""
    slide_num = slide["slide_number"]
    slide_title = slide["title"]
    tag = f"SLIDE {slide_num:02d}"

    resolution_label = {"512": "512px", "1k": "1K", "2k": "2K", "4k": "4K"}[resolution]
    prompt = f"Generate this image at {resolution_label} resolution.\n\n{slide['prompt']}"

    log(f"Sending request ({len(prompt):,} chars) — {slide_title}", tag)

    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)],
        ),
    ]

    config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_level="HIGH"),
        response_modalities=["IMAGE", "TEXT"],
    )

    t0 = time.time()
    chunks_received = 0
    bytes_received = 0
    text_parts = []
    usage = None
    saved_path = None

    for chunk in client.models.generate_content_stream(
        model=IMAGE_MODEL,
        contents=contents,
        config=config,
    ):
        chunks_received += 1
        elapsed = time.time() - t0

        if getattr(chunk, "usage_metadata", None):
            usage = chunk.usage_metadata

        if chunk.parts is None:
            log(f"Chunk {chunks_received}: (empty, {elapsed:.1f}s elapsed)", tag)
            continue

        for part in chunk.parts:
            if part.inline_data and part.inline_data.data:
                data = part.inline_data.data
                bytes_received += len(data)
                size_kb = len(data) / 1024
                size_mb = len(data) / (1024 * 1024)
                if size_mb >= 1:
                    size_str = f"{size_mb:.1f} MB"
                else:
                    size_str = f"{size_kb:.0f} KB"

                log(
                    f"Received image data: {size_str} "
                    f"(mime: {part.inline_data.mime_type}, "
                    f"{elapsed:.1f}s elapsed)",
                    tag,
                )

                ext = mimetypes.guess_extension(part.inline_data.mime_type) or ".png"
                saved_path = os.path.join(
                    output_dir, f"slide_{slide_num:02d}{ext}"
                )
                save_binary_file(saved_path, data)
                log(f"Saved: {saved_path} ({size_str})", tag)

            elif part.text:
                text_parts.append(part.text)
                log(f"Chunk {chunks_received}: text response ({len(part.text)} chars, {elapsed:.1f}s)", tag)

    slide_cost, slide_breakdown = compute_cost(IMAGE_MODEL, usage)
    if slide_breakdown:
        log(
            f"Cost: ${slide_cost:.4f} "
            f"(in:{slide_breakdown['input_tokens']} "
            f"out:{slide_breakdown['output_tokens']} "
            f"think:{slide_breakdown['thinking_tokens']} "
            f"img:{slide_breakdown['image_output_tokens']} tokens)",
            tag,
        )

    if saved_path:
        return saved_path, slide_cost

    # If we got text but no image, log it
    if text_parts:
        full_text = "".join(text_parts)
        log(f"Model returned text only: {full_text[:200]}...", tag)

    raise RuntimeError(f"No image generated for slide {slide_num}: {slide_title}")


def build_pptx(slides, output_dir, pptx_path):
    """Assemble generated slide images into a PowerPoint file with speaker notes."""
    prs = Presentation()
    # Set 16:9 slide dimensions (standard widescreen)
    prs.slide_width = Emu(12192000)   # 13.333 inches
    prs.slide_height = Emu(6858000)   # 7.5 inches

    blank_layout = prs.slide_layouts[6]  # blank layout

    for slide_data in sorted(slides, key=lambda s: s["slide_number"]):
        slide_num = slide_data["slide_number"]
        # Find the generated image file
        image_path = None
        for ext in (".png", ".jpg", ".jpeg", ".webp"):
            candidate = os.path.join(output_dir, f"slide_{slide_num:02d}{ext}")
            if os.path.exists(candidate):
                image_path = candidate
                break

        if not image_path:
            log(f"No image found for slide {slide_num}, skipping", "PPTX")
            continue

        pptx_slide = prs.slides.add_slide(blank_layout)
        # Add image covering the full slide
        pptx_slide.shapes.add_picture(
            image_path, Emu(0), Emu(0),
            width=prs.slide_width, height=prs.slide_height,
        )

        # Add speaker notes if available
        notes = slide_data.get("speaker_notes")
        if notes:
            notes_slide = pptx_slide.notes_slide
            notes_slide.notes_text_frame.text = notes

    prs.save(pptx_path)
    log(f"PowerPoint saved: {pptx_path}", "PPTX")
    return pptx_path


def ocr_slide_image(image_path):
    """Use macOS Vision framework to OCR text from a slide image."""
    import Quartz
    import Vision

    url = Quartz.CFURLCreateWithFileSystemPath(
        None, image_path, Quartz.kCFURLPOSIXPathStyle, False
    )
    source = Quartz.CGImageSourceCreateWithURL(url, None)
    if source is None:
        log(f"Could not load image: {image_path}", "OCR")
        return []
    image = Quartz.CGImageSourceCreateImageAtIndex(source, 0, None)
    if image is None:
        log(f"Could not create image from source: {image_path}", "OCR")
        return []

    request = Vision.VNRecognizeTextRequest.alloc().init()
    request.setRecognitionLevel_(Vision.VNRequestTextRecognitionLevelAccurate)

    handler = Vision.VNImageRequestHandler.alloc().initWithCGImage_options_(image, None)
    success, error = handler.performRequests_error_([request], None)
    if not success:
        log(f"OCR failed for {image_path}: {error}", "OCR")
        return []

    results = request.results()
    lines = []
    for observation in results:
        candidates = observation.topCandidates_(1)
        if candidates:
            lines.append(candidates[0].string())

    return lines


def build_ocr_markdown(slides, output_dir, markdown_path):
    """OCR each slide image and write a formatted markdown file."""
    log("Starting OCR on slide images...", "OCR")
    md_lines = ["# Slide Deck — OCR Transcript\n"]

    for slide_data in sorted(slides, key=lambda s: s["slide_number"]):
        slide_num = slide_data["slide_number"]
        slide_title = slide_data.get("title", f"Slide {slide_num}")

        # Find the generated image
        image_path = None
        for ext in (".png", ".jpg", ".jpeg", ".webp"):
            candidate = os.path.join(output_dir, f"slide_{slide_num:02d}{ext}")
            if os.path.exists(candidate):
                image_path = candidate
                break

        if not image_path:
            log(f"No image for slide {slide_num}, skipping OCR", "OCR")
            continue

        log(f"OCR slide {slide_num}: {slide_title}", "OCR")
        text_lines = ocr_slide_image(image_path)

        md_lines.append(f"---\n\n## Slide {slide_num}: {slide_title}\n")
        if text_lines:
            for line in text_lines:
                md_lines.append(f"{line}\n")
        else:
            md_lines.append("*(no text detected)*\n")
        md_lines.append("")

    content = "\n".join(md_lines)
    with open(markdown_path, "w") as f:
        f.write(content)
    log(f"OCR markdown saved: {markdown_path}", "OCR")
    return markdown_path


def generate_all_slides(client, slides, resolution, output_dir, max_parallel):
    """Generate all slide images in parallel. Returns (paths, total_cost, per_slide_costs)."""
    os.makedirs(output_dir, exist_ok=True)
    total = len(slides)
    completed = 0
    failed = 0
    results = []
    total_cost = 0.0
    per_slide_costs = {}

    log(f"Starting {total} image generations with {max_parallel} workers", "GEN")
    log(f"Output directory: {output_dir}", "GEN")
    t0 = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_parallel) as executor:
        futures = {
            executor.submit(generate_slide_image, client, slide, resolution, output_dir): slide
            for slide in slides
        }

        log(f"All {total} tasks submitted to thread pool", "GEN")

        for future in concurrent.futures.as_completed(futures):
            slide = futures[future]
            try:
                path, slide_cost = future.result()
                completed += 1
                results.append(path)
                total_cost += slide_cost
                per_slide_costs[slide["slide_number"]] = slide_cost
                elapsed = time.time() - t0
                log(
                    f"[{completed + failed}/{total}] OK — slide {slide['slide_number']:02d} "
                    f"({slide['title']}) — ${slide_cost:.4f} — {elapsed:.1f}s total",
                    "GEN",
                )
            except Exception as e:
                failed += 1
                elapsed = time.time() - t0
                log(
                    f"[{completed + failed}/{total}] FAILED — slide {slide['slide_number']:02d} "
                    f"({slide['title']}): {e} — {elapsed:.1f}s total",
                    "GEN",
                )

    elapsed = time.time() - t0
    log(f"Generation complete: {completed} succeeded, {failed} failed in {elapsed:.1f}s", "GEN")
    log(f"Image generation cost: ${total_cost:.4f}", "GEN")
    return results, total_cost, per_slide_costs


def main():
    args = parse_args()

    selected_slides = None
    if args.slides:
        selected_slides = parse_slide_numbers(args.slides)

    log(f"Pitch Deck Maker starting", "MAIN")
    log(f"  Deck file:    {args.deck_file}", "MAIN")
    log(f"  Output dir:   {args.output}", "MAIN")
    log(f"  Resolution:   {args.resolution}", "MAIN")
    log(f"  Max parallel: {args.max_parallel}", "MAIN")
    if args.all:
        slides_label = "all"
    elif any(isinstance(x, tuple) for x in selected_slides):
        start = next(x[1] for x in selected_slides if isinstance(x, tuple))
        slides_label = f"{start}+"
    else:
        slides_label = str(sorted(selected_slides))
    log(f"  Slides:       {slides_label}", "MAIN")
    log(f"  Parse model:  {PARTITION_MODEL}", "MAIN")
    log(f"  Image model:  {IMAGE_MODEL}", "MAIN")

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        log("GEMINI_API_KEY environment variable is not set!", "ERROR")
        sys.exit(1)
    log(f"API key loaded ({len(api_key)} chars)", "MAIN")

    client = genai.Client(api_key=api_key)
    log("Gemini client initialized", "MAIN")

    log(f"Reading deck file: {args.deck_file}", "MAIN")
    with open(args.deck_file) as f:
        markdown_content = f.read()
    log(f"Deck loaded: {len(markdown_content):,} chars, {markdown_content.count(chr(10)):,} lines", "MAIN")

    log("=" * 60, "MAIN")
    log("PHASE 1: PARSING DECK INTO SLIDE PROMPTS", "MAIN")
    log("=" * 60, "MAIN")
    all_slides, parse_cost = partition_deck(client, markdown_content)
    log(f"Found {len(all_slides)} slides with image prompts", "MAIN")

    # Resolve range sentinels (e.g. 3+) now that we know total slide count
    if selected_slides:
        max_slide = max(s["slide_number"] for s in all_slides)
        selected_slides = resolve_slide_range(selected_slides, max_slide)

    # Filter to selected slides if specified
    if selected_slides:
        slides = [s for s in all_slides if s["slide_number"] in selected_slides]
        missing = selected_slides - {s["slide_number"] for s in all_slides}
        if missing:
            log(f"Warning: slide numbers not found in deck: {sorted(missing)}", "MAIN")
        log(f"Selected {len(slides)} of {len(all_slides)} slides for generation", "MAIN")
    else:
        slides = all_slides

    log("=" * 60, "MAIN")
    log("PHASE 2: GENERATING SLIDE IMAGES", "MAIN")
    log("=" * 60, "MAIN")
    results, gen_cost, per_slide_costs = generate_all_slides(
        client, slides, args.resolution, args.output, args.max_parallel
    )

    log("=" * 60, "MAIN")
    log("PHASE 3: ASSEMBLING POWERPOINT", "MAIN")
    log("=" * 60, "MAIN")
    deck_name = os.path.splitext(os.path.basename(args.deck_file))[0]
    pptx_path = os.path.join(args.output, f"{deck_name}.pptx")
    build_pptx(slides, args.output, pptx_path)

    log("=" * 60, "MAIN")
    log("PHASE 4: OCR SLIDE IMAGES → MARKDOWN", "MAIN")
    log("=" * 60, "MAIN")
    ocr_md_path = os.path.join(args.output, f"{deck_name}_ocr.md")
    build_ocr_markdown(slides, args.output, ocr_md_path)

    # Cost summary
    total_cost = parse_cost + gen_cost
    log("=" * 60, "MAIN")
    log("COST SUMMARY", "COST")
    log("-" * 40, "COST")
    log(f"  Parsing:              ${parse_cost:.4f}", "COST")
    log(f"  Image generation:     ${gen_cost:.4f}", "COST")
    for slide_num in sorted(per_slide_costs):
        cost = per_slide_costs[slide_num]
        title = next(
            (s["title"] for s in slides if s["slide_number"] == slide_num), ""
        )
        log(f"    Slide {slide_num:2d}: ${cost:.4f}  {title}", "COST")
    log("-" * 40, "COST")
    log(f"  TOTAL:                ${total_cost:.4f}", "COST")

    log("=" * 60, "MAIN")
    log(f"DONE: {len(results)}/{len(slides)} images saved to {args.output}/", "MAIN")
    log(f"      PowerPoint: {pptx_path}", "MAIN")
    log(f"      OCR markdown: {ocr_md_path}", "MAIN")
    log("=" * 60, "MAIN")


if __name__ == "__main__":
    main()
