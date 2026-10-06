"""Convert source-prepped.png into a monochrome ASCII SVG that types itself in once."""
import os
from pathlib import Path
from xml.sax.saxutils import escape

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source-prepped.png"
OUT = ROOT / "suhaas-ascii.svg"

RAMP = " .`:-=+*cs#%@"  # bright (sparse) -> dark (dense)
COLS, ROWS = 100, 53
CHAR_W, LINE_H, FONT_SIZE = 6.0, 12, 10
PAD = 14
FILL = "#c9d1d9"
FONT = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"
STATIC = os.environ.get("STATIC") == "1"


def to_grid(image):
    # Fit inside COLS x ROWS; a glyph cell is twice as tall as it is wide.
    cell_aspect = LINE_H / CHAR_W
    scale = min(COLS / image.width, ROWS * cell_aspect / image.height)
    cols = max(1, round(image.width * scale))
    rows = max(1, round(image.height * scale / cell_aspect))
    pixels = np.asarray(image.resize((cols, rows), Image.LANCZOS), dtype=np.float32)

    lo, hi = np.percentile(pixels, (2, 98))
    pixels = np.clip((pixels - lo) / max(hi - lo, 1), 0, 1)
    index = np.round((1 - pixels) * (len(RAMP) - 1)).astype(int)

    grid = np.full((ROWS, COLS), " ")
    top, left = (ROWS - rows) // 2, (COLS - cols) // 2
    grid[top : top + rows, left : left + cols] = np.array(list(RAMP))[index]
    return ["".join(row).rstrip() for row in grid]


def main():
    lines = to_grid(Image.open(SRC).convert("L"))
    text_w = COLS * CHAR_W
    width, height = text_w + 2 * PAD, ROWS * LINE_H + 2 * PAD
    row_time, stagger = 0.5, 0.055

    clips, rows = [], []
    for i, line in enumerate(lines):
        if not line:
            continue
        y = PAD + i * LINE_H
        begin = i * stagger
        row_w = len(line) * CHAR_W
        text = (
            f'<text x="{PAD}" y="{y + FONT_SIZE}" textLength="{row_w}" lengthAdjust="spacingAndGlyphs" '
            f'xml:space="preserve">{escape(line)}</text>'
        )
        if STATIC:
            rows.append(text)
            continue
        clips.append(
            f'<clipPath id="r{i}"><rect x="{PAD}" y="{y}" width="0" height="{LINE_H}">'
            f'<animate attributeName="width" from="0" to="{row_w}" begin="{begin:.3f}s" dur="{row_time}s" fill="freeze"/>'
            f"</rect></clipPath>"
        )
        cursor = (
            f'<rect y="{y + 1}" width="{CHAR_W}" height="{LINE_H - 2}" fill="{FILL}" opacity="0">'
            f'<animate attributeName="x" from="{PAD}" to="{PAD + row_w}" begin="{begin:.3f}s" dur="{row_time}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="1" begin="{begin:.3f}s" dur="{row_time}s"/>'
            f"</rect>"
        )
        rows.append(f'<g clip-path="url(#r{i})">{text}</g>{cursor}')

    OUT.write_text(
        f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:g} {height}" width="{width:g}" height="{height}" role="img" aria-label="ASCII portrait">
<rect x=".5" y=".5" width="{width - 1:g}" height="{height - 1}" rx="10" fill="#0d1117" stroke="#30363d"/>
<defs>{''.join(clips)}</defs>
<g fill="{FILL}" font-family="{FONT}" font-size="{FONT_SIZE}">
{''.join(rows)}
</g>
</svg>
"""
    )
    print(f"{len(rows)} rows -> {OUT}")


if __name__ == "__main__":
    main()
