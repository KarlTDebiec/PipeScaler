#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Compare exact CPU and WGSL mask filling on reproducible synthetic masks.

Run from the repository root with
`uv run python -m test.scripts.benchmark_mask_filler --sizes 16 32 64 128`.
Timings include image conversion, transfers, and completion readbacks. Shader
startup is reported separately from median warmed execution times.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable
from statistics import median
from time import perf_counter
from unittest.mock import patch

import numpy as np
from PIL import Image
from wgpu.utils import get_default_device

from pipescaler.image.core.enums import MaskFillMode
from pipescaler.image.utilities.mask_filler import MaskFiller


def _main():
    """Print cold startup and verified median execution times for each mask."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", type=int, nargs="+", default=[16, 32, 64, 128])
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()
    if args.repeats < 1 or min(args.sizes) < 3:
        parser.error("repeats must be positive and sizes must be at least 3")

    image = Image.new("L", (3, 3))
    mask = Image.new("1", image.size)
    mask.putpixel((1, 1), 1)
    start = perf_counter()
    with (
        patch.object(MaskFiller, "_minimum_shader_pixels", 0),
        patch.object(MaskFiller, "run_iteration", side_effect=AssertionError),
    ):
        MaskFiller.run(image, mask, MaskFillMode.BASIC)
    print(f"Shader cold startup: {(perf_counter() - start) * 1000:.2f} ms")
    print(f"Adapter: {dict(get_default_device().adapter.info)}")
    print("mode,size,mask,cpu_ms,wgsl_ms,speedup")
    for mode in ("L", "RGB"):
        for size in args.sizes:
            rng = np.random.default_rng(792)
            shape = (size, size) if mode == "L" else (size, size, 3)
            image = Image.fromarray(rng.integers(0, 256, shape, dtype=np.uint8))
            single_pixel = np.zeros((size, size), dtype=bool)
            single_pixel[size // 2, size // 2] = True
            interior_hole = np.ones((size, size), dtype=bool)
            interior_hole[[0, -1], :] = False
            interior_hole[:, [0, -1]] = False
            for name, mask_arr in (
                ("single_pixel", single_pixel),
                ("random_half", rng.random((size, size)) < 0.5),
                ("interior_hole", interior_hole),
                ("single_seed", ~single_pixel),
            ):
                mask = Image.fromarray(mask_arr)
                with patch.object(
                    MaskFiller, "_minimum_shader_pixels", mask_arr.size + 1
                ):
                    expected = MaskFiller.run(image, mask, MaskFillMode.BASIC)
                    cpu_time = _measure(
                        lambda: MaskFiller.run(image, mask, MaskFillMode.BASIC),
                        args.repeats,
                    )
                with (
                    patch.object(MaskFiller, "_minimum_shader_pixels", 0),
                    patch.object(
                        MaskFiller, "run_iteration", side_effect=AssertionError
                    ),
                ):
                    np.testing.assert_array_equal(
                        np.asarray(MaskFiller.run(image, mask, MaskFillMode.BASIC)),
                        np.asarray(expected),
                    )
                    shader_time = _measure(
                        lambda: MaskFiller.run(image, mask, MaskFillMode.BASIC),
                        args.repeats,
                    )
                print(
                    f"{mode},{size},{name},{cpu_time * 1000:.3f},"
                    f"{shader_time * 1000:.3f},{cpu_time / shader_time:.2f}"
                )


def _measure(operation: Callable[[], Image.Image], repeats: int) -> float:
    """Measure median wall time for a complete synchronous image operation.

    Arguments:
        operation: image operation including any CPU/GPU transfers
        repeats: number of measured calls
    Returns:
        median elapsed time in seconds
    """
    elapsed = []
    for _ in range(repeats):
        start = perf_counter()
        operation()
        elapsed.append(perf_counter() - start)
    return median(elapsed)


if __name__ == "__main__":
    _main()
