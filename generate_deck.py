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


PARTITION_MODEL = "gemini-2.5-flash-lite"
IMAGE_MODEL = "gemini-3.1-flash-image-preview"

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
        description="Generate slide deck images from a markdown file using Gemini."
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
        default=5,
        help="Max concurrent image generations (default: 5)",
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
        help="Comma-separated slide numbers to generate (e.g. 3,5,6,10)",
    )

    return parser.parse_args()


def parse_slide_numbers(slides_str):
    """Parse '3,5,6,10' into a set of ints."""
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


def partition_deck(client, markdown_content):
    """Use Gemini Flash Lite to parse the deck into individual slide prompts."""
    prompt_text = PARTITION_PROMPT + markdown_content
    log(f"Sending {len(prompt_text):,} chars to {PARTITION_MODEL} for parsing...", "PARSE")

    t0 = time.time()

    # Stream the partition response so we can show progress
    chunks_received = 0
    json_text = ""

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

    elapsed = time.time() - t0
    log(
        f"Partition complete: {len(json_text):,} chars in {elapsed:.1f}s "
        f"({chunks_received} chunks)",
        "PARSE",
    )

    slides = json.loads(json_text)
    # Validate structure
    for slide in slides:
        if not all(k in slide for k in ("slide_number", "title", "prompt")):
            raise ValueError(f"Invalid slide entry missing required fields: {slide}")

    for s in slides:
        log(f"  Slide {s['slide_number']:2d}: {s['title']} ({len(s['prompt']):,} char prompt)", "PARSE")

    return slides


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
        thinking_config=types.ThinkingConfig(thinking_level="MINIMAL"),
        response_modalities=["IMAGE", "TEXT"],
    )

    t0 = time.time()
    chunks_received = 0
    bytes_received = 0
    text_parts = []

    for chunk in client.models.generate_content_stream(
        model=IMAGE_MODEL,
        contents=contents,
        config=config,
    ):
        chunks_received += 1
        elapsed = time.time() - t0

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
                file_path = os.path.join(
                    output_dir, f"slide_{slide_num:02d}{ext}"
                )
                save_binary_file(file_path, data)
                log(f"Saved: {file_path} ({size_str})", tag)
                return file_path

            elif part.text:
                text_parts.append(part.text)
                log(f"Chunk {chunks_received}: text response ({len(part.text)} chars, {elapsed:.1f}s)", tag)

    # If we got text but no image, log it
    if text_parts:
        full_text = "".join(text_parts)
        log(f"Model returned text only: {full_text[:200]}...", tag)

    raise RuntimeError(f"No image generated for slide {slide_num}: {slide_title}")


def generate_all_slides(client, slides, resolution, output_dir, max_parallel):
    """Generate all slide images in parallel."""
    os.makedirs(output_dir, exist_ok=True)
    total = len(slides)
    completed = 0
    failed = 0
    results = []

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
                path = future.result()
                completed += 1
                results.append(path)
                elapsed = time.time() - t0
                log(
                    f"[{completed + failed}/{total}] OK — slide {slide['slide_number']:02d} "
                    f"({slide['title']}) — {elapsed:.1f}s total",
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
    return results


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
    log(f"  Slides:       {('all' if args.all else sorted(selected_slides))}", "MAIN")
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
    all_slides = partition_deck(client, markdown_content)
    log(f"Found {len(all_slides)} slides with image prompts", "MAIN")

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
    results = generate_all_slides(client, slides, args.resolution, args.output, args.max_parallel)

    log("=" * 60, "MAIN")
    log(f"DONE: {len(results)}/{len(slides)} images saved to {args.output}/", "MAIN")
    log("=" * 60, "MAIN")


if __name__ == "__main__":
    main()
