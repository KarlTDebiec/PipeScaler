#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for ThresholdProcessor."""

from __future__ import annotations

import numpy as np
import pytest
from PIL import Image

from pipescaler.image.operators.processors import ThresholdProcessor
from pipescaler.image.testing import xfail_unsupported_image_mode
from pipescaler.testing.file import get_test_input_path
from pipescaler.testing.fixture import parametrized_fixture


@parametrized_fixture(
    cls=ThresholdProcessor,
    params=[
        {"threshold": 128, "denoise": False},
        {"threshold": 128, "denoise": True},
    ],
)
def processor(request: pytest.FixtureRequest) -> ThresholdProcessor:
    """Pytest fixture that provides a ThresholdProcessor instance.

    Arguments:
        request: Pytest request fixture containing parameters
    Returns:
        Configured ThresholdProcessor instance
    """
    return ThresholdProcessor(**request.param)


@pytest.mark.parametrize(
    "input_filename",
    [
        "1",
        "L",
        xfail_unsupported_image_mode()("LA"),
        xfail_unsupported_image_mode()("RGB"),
        xfail_unsupported_image_mode()("RGBA"),
        "PL",
        xfail_unsupported_image_mode()("PLA"),
        xfail_unsupported_image_mode()("PRGB"),
        xfail_unsupported_image_mode()("PRGBA"),
    ],
)
def test(input_filename: str, processor: ThresholdProcessor):
    """Test ThresholdProcessor with various image modes.

    Arguments:
        input_filename: Input image filename
        processor: ThresholdProcessor fixture instance
    """
    input_path = get_test_input_path(input_filename)
    input_img = Image.open(input_path)
    output_img = processor(input_img)

    output_arr = np.array(output_img)
    assert output_img.size == input_img.size
    if input_img.mode == "1":
        assert output_img.mode == "1"
    else:
        assert output_img.mode == "L"
        assert np.logical_or(output_arr == 0, output_arr == 255).all()


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
    assert np.array(output_image).flatten().tolist() == expected


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

    assert output_image.mode == mode
    assert np.array_equal(np.array(output_image), np.array(input_image))


@pytest.mark.parametrize("mode", ["1", "L"])
def test_denoise_removes_isolated_white_pixel(mode: str):
    """Denoising removes an isolated white pixel in supported modes.

    Arguments:
        mode: input image mode
    """
    if mode == "1":
        dtype = bool
    else:
        dtype = np.uint8
    input_array = np.zeros((5, 5), dtype=dtype)
    input_array[2, 2] = 255
    input_image = Image.fromarray(input_array)

    output_image = ThresholdProcessor(denoise=True)(input_image)

    assert output_image.mode == mode
    assert np.array_equal(np.array(output_image), np.zeros((5, 5), dtype=dtype))
