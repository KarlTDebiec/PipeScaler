#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Generate tiny static frames with distinct colors and alpha for APNG tests."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

__all__ = ["write_apng_frames"]


def write_apng_frames(dir_path: Path) -> list[Path]:
    """Write three frames whose changing regions exercise APNG composition.

    Arguments:
        dir_path: directory for generated PNGs, created if necessary
    Returns:
        frame paths in playback order, intentionally different from filename order
    """
    dir_path.mkdir(parents=True, exist_ok=True)
    paths = []
    for index, (name, color) in enumerate(
        zip(
            ("z first", "a second", "m third"),
            ((255, 0, 0, 255), (0, 255, 0, 128), (0, 0, 255, 255)),
            strict=True,
        )
    ):
        image = Image.new("RGBA", (8, 6), (0, 0, 0, 0))
        image.paste(color, (index + 1, 1, index + 5, 4))
        image.putpixel((6, 4), (255, 255, 255, 255))
        path = dir_path / f"{name}.png"
        image.save(path)
        paths.append(path)
    return paths
