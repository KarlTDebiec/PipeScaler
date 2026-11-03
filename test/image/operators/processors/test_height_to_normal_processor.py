#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for HeightToNormalProcessor."""

from __future__ import annotations

import warnings

import numpy as np
import pytest
from PIL import Image

from pipescaler.image.core.functions import generate_normal_map_from_height_map_image
from pipescaler.image.operators.processors import HeightToNormalProcessor
from pipescaler.image.testing import xfail_unsupported_image_mode
from pipescaler.testing.file import get_test_input_path
from pipescaler.testing.fixture import parametrized_fixture


@parametrized_fixture(
    cls=HeightToNormalProcessor,
    params=[{"sigma": None}, {"sigma": 1.0}],
)
def processor(request: pytest.FixtureRequest) -> HeightToNormalProcessor:
    """Pytest fixture that provides a HeightToNormalProcessor instance.

    Arguments:
        request: Pytest request fixture containing parameters
    Returns:
        Configured HeightToNormalProcessor instance
    """
    return HeightToNormalProcessor(**request.param)


@pytest.mark.parametrize(
    "input_filename",
    [
        xfail_unsupported_image_mode()("1"),
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
def test(input_filename: str, processor: HeightToNormalProcessor):
    """Test HeightToNormalProcessor with various height map modes.

    Arguments:
        input_filename: Input image filename
        processor: HeightToNormalProcessor fixture instance
    """
    input_path = get_test_input_path(input_filename)
    input_img = Image.open(input_path)
    output_img = processor(input_img)

    output_datum = np.array(output_img)
    assert output_img.mode == "RGB"
    assert output_img.size == input_img.size
    assert np.min(output_datum[:, :, 2] >= 128)


@pytest.mark.parametrize("shape", [(1, 1), (3, 4)])
def test_flat_height_map_generates_upward_normals(shape: tuple[int, int]):
    """Test flat height maps generate neutral x and y channels without warnings.

    Arguments:
        shape: height map dimensions
    """
    input_image = Image.fromarray(np.zeros(shape, dtype=np.uint8))

    with warnings.catch_warnings():
        warnings.simplefilter("error", RuntimeWarning)
        output_image = generate_normal_map_from_height_map_image(input_image)

    output_array = np.asarray(output_image)
    assert output_image.mode == "RGB"
    assert output_image.size == input_image.size
    assert np.all(output_array == [128, 128, 255])


@pytest.mark.parametrize(("step", "expected_sign"), [(1, -1), (-1, 1)])
def test_height_ramp_normal_uses_signed_gradient(step: int, expected_sign: int):
    """Test increasing and decreasing height ramps retain their gradient sign.

    Arguments:
        step: height change between adjacent columns
        expected_sign: expected sign of the encoded x normal
    """
    input_array = np.tile(128 + np.arange(5, dtype=np.int16) * step, (5, 1))
    input_image = Image.fromarray(input_array.astype(np.uint8))

    output_array = np.asarray(generate_normal_map_from_height_map_image(input_image))
    assert (int(output_array[2, 2, 0]) - 128) * expected_sign > 0
    assert output_array[2, 2, 2] >= 128
