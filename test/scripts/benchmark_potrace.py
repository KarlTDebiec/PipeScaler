#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Compare native tracing with potracer on generated logos and repeated detail.

Run `uv run --with potracer python test/scripts/benchmark_potrace.py` after
configuring libpotrace. Timings include bitmap conversion and curve copying;
neither implementation rasterizes. Python 3.14 is used for both implementations.
"""

from __future__ import annotations

from importlib import import_module
from statistics import median
from time import perf_counter

import numpy as np
from PIL import Image, ImageDraw

from pipescaler.image.utilities.potrace import trace_bitmap

__all__ = ["benchmark"]


def benchmark():
    """Print median elapsed seconds for three traces of each generated image."""
    potrace = import_module("potrace")
    print("size,content,native_seconds,python_seconds")
    for size in (64, 256):
        for content in ("logo", "detail"):
            image = Image.new("L", (size, size), 255)
            draw = ImageDraw.Draw(image)
            if content == "logo":
                draw.ellipse(
                    (size // 8, size // 8, size * 7 // 8, size * 7 // 8), fill=0
                )
                draw.rectangle(
                    (size // 3, size // 3, size * 2 // 3, size * 2 // 3), fill=255
                )
            else:
                for y in range(0, size, 16):
                    for x in range(0, size, 16):
                        draw.ellipse((x, y, x + 10, y + 10), fill=0)
            native_times = []
            python_times = []
            for _ in range(3):
                start = perf_counter()
                trace_bitmap(
                    np.asarray(image) < 255 * 0.3,
                    turdsize=2,
                    turnpolicy=4,
                    alphamax=1.34,
                    opticurve=True,
                    opttolerance=0.2,
                )
                native_times.append(perf_counter() - start)
                start = perf_counter()
                potrace.Bitmap(image, blacklevel=0.3).trace(alphamax=1.34)
                python_times.append(perf_counter() - start)
            print(
                f"{size},{content},{median(native_times):.6f},{median(python_times):.6f}"
            )


if __name__ == "__main__":
    benchmark()
