# Pitch Deck Maker

Generate visual slide deck images from a markdown file using Google Gemini.

## Prerequisites

- Python 3.10+
- A [Gemini API key](https://aistudio.google.com/apikey)

## Setup

```bash
pip install -r requirements.txt
export GEMINI_API_KEY=your_api_key_here
```

## Usage

```bash
python generate_deck.py <deck_file> [options]
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `--all` | Generate all slides (required if `--slides` not used) | — |
| `--slides` | Comma-separated slide numbers to generate (e.g. `3,5,6,10`) | — |
| `-o`, `--output` | Output directory for generated images | `./output` |
| `-r`, `--resolution` | Image resolution: `512`, `1k`, `2k`, `4k` | `512` |
| `-p`, `--max-parallel` | Max concurrent image generations | `5` |

You must specify either `--all` or `--slides`.

### Examples

```bash
# Generate all slides at default 512px resolution
python generate_deck.py example-deck.md --all

# Regenerate specific slides
python generate_deck.py example-deck.md --slides 3,5,6,10

# Generate all at 2K resolution into a custom directory
python generate_deck.py example-deck.md --all -r 2k -o ./slides

# Generate specific slides at 4K with more parallelism
python generate_deck.py example-deck.md --slides 1,2,3 -r 4k -p 10 -o ./slides-4k
```

## Markdown Deck Format

See `example-deck.md` for a complete example. The format:

1. **Global style directive** — a blockquote before the first `---` that defines the visual style for all slides:
   ```
   > *[SLIDE FORMAT: 16:9. Clean white background. Navy blue ink, hand-drawn style...]*
   ```

2. **Slides separated by `---`** — each slide has:
   - A heading: `## Slide Title`
   - A visual directive in a blockquote: `> *[VISUAL — description of what to generate...]*`
   - Optional speaking notes: `**SPEAKING NOTES:** ...`

Only slides with a `[VISUAL ...]` directive will have images generated. The tool uses Gemini Flash to parse the markdown and merge the global style with each slide's visual description, then generates all slide images in parallel using Gemini's image generation model.

## Output

Images are saved as `slide_01.png`, `slide_02.png`, etc. in the output directory, numbered by their position in the deck.
