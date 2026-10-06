"""Isolate the subject, boost local contrast, and flatten onto white for ASCII conversion.

Usage: python scripts/prep_photo.py source-photo.jpg
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove

OUT = Path(__file__).resolve().parent.parent / "source-prepped.png"


def main(path):
    cutout = remove(Image.open(path).convert("RGBA"))
    rgba = np.array(cutout)
    alpha = rgba[..., 3:4].astype(np.float32) / 255

    gray = cv2.cvtColor(rgba[..., :3], cv2.COLOR_RGB2GRAY)
    gray = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8)).apply(gray)

    # White background maps to the blank end of the ASCII ramp.
    flat = gray[..., None].astype(np.float32) * alpha + 255 * (1 - alpha)
    flat = flat[..., 0].astype(np.uint8)

    # Crop to the subject so the portrait fills the grid.
    ys, xs = np.where(alpha[..., 0] > 0.05)
    if len(ys):
        flat = flat[ys.min() : ys.max() + 1, xs.min() : xs.max() + 1]

    Image.fromarray(flat).save(OUT)
    print(f"-> {OUT}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
