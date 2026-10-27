#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Behavior-preserving reconstruction of image processor representations."""

from __future__ import annotations

from typing import Literal, cast

import pytest
from PIL import Image

from pipescaler.image.operators.processors.mode_processor import ModeProcessor
from pipescaler.image.operators.processors.resize_processor import ResizeProcessor


@pytest.mark.parametrize("background_color", ["#000000", "papayawhip", "#2468ac80"])
@pytest.mark.parametrize("mode", ["1", "L", "LA", "RGB", "RGBA"])
def test_mode_representation_round_trip(
    background_color: str, mode: Literal["1", "L", "LA", "RGB", "RGBA"]
):
    """Reconstruct conversion settings, background alpha, and binary threshold.

    Arguments:
        background_color: background color accepted by Pillow
        mode: target image mode
    """
    processor = ModeProcessor(mode, background_color, threshold=200)
    reconstructed = cast("ModeProcessor", eval(repr(processor)))
    input_image = Image.frombytes(
        "RGBA", (3, 1), bytes([255, 0, 0, 0, 20, 100, 240, 128, 170, 170, 170, 255])
    )

    assert reconstructed.mode == processor.mode
    assert reconstructed.background_color == processor.background_color
    assert reconstructed.threshold == processor.threshold
    expected = processor(input_image)
    actual = reconstructed(input_image)
    assert actual.mode == expected.mode
    assert actual.size == expected.size
    assert actual.tobytes() == expected.tobytes()


@pytest.mark.parametrize("resample", ["bicubic", "bilinear", "lanczos", "nearest"])
@pytest.mark.parametrize("scale", [0.5, 1.5, 2.0])
@pytest.mark.parametrize("mode", ["1", "L", "LA", "RGB", "RGBA"])
def test_resize_representation_round_trip(resample: str, scale: float, mode: str):
    """Reconstruct resize settings and preserve filtered output pixels.

    Arguments:
        resample: supported resampling algorithm
        scale: output scale relative to input
        mode: input image mode
    """
    processor = ResizeProcessor(scale, resample)
    reconstructed = cast("ResizeProcessor", eval(repr(processor)))
    input_image = Image.frombytes("RGBA", (4, 3), bytes(range(0, 240, 5))).convert(mode)

    assert reconstructed.scale == processor.scale
    assert reconstructed.resample == processor.resample
    expected = processor(input_image)
    actual = reconstructed(input_image)
    assert actual.mode == expected.mode
    assert actual.size == expected.size
    assert actual.tobytes() == expected.tobytes()
