#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for ThresholdProcessor."""

from __future__ import annotations

import numpy as np
import pytest
from PIL import Image

from pipescaler.image.operators.processors import ThresholdProcessor


@pytest.mark.parametrize(
    ("threshold", "expected"),
    [(1, [0, 0, 255, 255, 255, 255]), (244, [0, 0, 0, 0, 255, 255])],
)
def test_threshold_processor_boundaries(threshold: int, expected: list[int]):
    """Preserve pixel comparisons at the existing threshold bounds.

    Arguments:
        threshold: supported cutoff value
        expected: expected binary pixels
    """
    image = Image.fromarray(np.array([[0, 1, 2, 244, 245, 255]], dtype=np.uint8))
    output_image = ThresholdProcessor(threshold)(image)
    assert np.array(output_image.convert("L")).flatten().tolist() == expected


@pytest.mark.parametrize("threshold", [-1, 0, 245, 255, 256])
def test_threshold_processor_rejects_out_of_range_values(threshold: int):
    """Preserve rejection of thresholds outside the supported range.

    Arguments:
        threshold: unsupported threshold
    """
    with pytest.raises(ValueError):
        ThresholdProcessor(threshold)


@pytest.mark.parametrize("mode", ["1", "L"])
@pytest.mark.parametrize("value", [0, 255])
def test_denoise_preserves_uniform_binary_images(mode: str, value: int):
    """Denoising preserves all-black and all-white images in supported modes.

    Arguments:
        mode: input image mode
        value: uniform binary pixel value
    """
    if mode == "1":
        dtype = bool
    else:
        dtype = np.uint8
    input_image = Image.fromarray(np.full((5, 5), value, dtype=dtype))

    output_image = ThresholdProcessor(denoise=True)(input_image)

    assert output_image.mode == "1"
    assert np.array_equal(
        np.array(output_image.convert("L")), np.array(input_image.convert("L"))
    )
