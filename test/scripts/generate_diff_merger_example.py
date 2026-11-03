#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Generate a reproducible texture comparison using the real diff merger."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from pipescaler.image.operators.mergers import DiffMerger


def main():
    """Write source textures, the merger output, and a labeled comparison sheet."""
    parser = ArgumentParser(description=__doc__)

    # Output arguments
    parser.add_argument(
        "--output-dir", type=Path, default=Path("local/diff_merger_example")
    )
    output_dir_path = parser.parse_args().output_dir
    output_dir_path.mkdir(parents=True, exist_ok=True)

    # Draw a small repeatable texture without requiring external assets
    rng = np.random.default_rng(824)
    baseline = Image.new("RGB", (128, 128), (38, 44, 51))
    draw = ImageDraw.Draw(baseline)
    for row in range(8):
        for col in range(4):
            x = col * 32 - (row % 2) * 16
            y = row * 16
            gray = int(rng.integers(75, 125))
            draw.rectangle(
                (x + 1, y + 1, x + 30, y + 14), fill=(gray + 12, gray + 5, gray)
            )
            draw.line(
                (x + 2, y + 2, x + 29, y + 2), fill=(gray + 35, gray + 25, gray + 18)
            )
    draw.rectangle((48, 44, 80, 84), fill=(30, 40, 49), outline=(180, 155, 90), width=2)
    draw.polygon([(64, 48), (75, 64), (64, 80), (53, 64)], fill=(35, 170, 165))
    draw.line([(64, 48), (64, 80)], fill=(130, 235, 220), width=2)

    # Enlarge unchanged pixels, then brighten one region and darken another
    comparison = baseline.resize((256, 256), Image.Resampling.NEAREST)
    pixels = np.asarray(comparison).astype(np.int16)
    pixels[24:104, 16:96] += 75
    pixels[152:232, 160:240] -= 75
    comparison = Image.fromarray(np.clip(pixels, 0, 255).astype(np.uint8))
    difference = DiffMerger()(baseline, comparison)
    baseline.save(output_dir_path / "baseline.png")
    comparison.save(output_dir_path / "comparison.png")
    difference.save(output_dir_path / "difference.png")

    # Compose a readable sheet while leaving the saved diff pixels unmodified
    sheet = Image.new("RGB", (1088, 526), "#111820")
    draw = ImageDraw.Draw(sheet)
    title_font = ImageFont.load_default(size=25)
    label_font = ImageFont.load_default(size=18)
    note_font = ImageFont.load_default(size=16)
    draw.text(
        (28, 22), "DiffMerger / texture comparison", font=title_font, fill="#edf3fa"
    )
    panels = [
        (baseline, "Baseline", "128 x 128"),
        (comparison, "Comparison", "256 x 256"),
        (difference, "Difference", "256 x 256"),
    ]
    for index, (image, title, size) in enumerate(panels):
        x = 28 + index * 356
        draw.text((x, 76), title, font=label_font, fill="#edf3fa")
        draw.text((x, 102), size, font=note_font, fill="#93a4b7")
        sheet.paste(image.resize((320, 320), Image.Resampling.NEAREST), (x, 136))
    draw.text((28, 478), "Nearest-neighbor alignment", font=note_font, fill="#93a4b7")
    draw.text((384, 478), "Two brightness edits", font=note_font, fill="#93a4b7")
    draw.text((740, 478), "Red: lighter   Blue: darker", font=note_font, fill="#edf3fa")
    sheet.save(output_dir_path / "example.png")


if __name__ == "__main__":
    main()
