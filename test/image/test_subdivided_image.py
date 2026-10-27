#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for SubdividedImage."""

from __future__ import annotations

import numpy as np
import pytest
from PIL import Image

from pipescaler.image import SubdividedImage
from pipescaler.image.core.operators import ImageProcessor
from pipescaler.image.operators.processors import (
    PotraceProcessor,
    XbrzProcessor,
)
from pipescaler.testing.file import get_test_input_path


@pytest.fixture
def xbrz_processor() -> XbrzProcessor:
    """Pytest fixture that provides an XbrzProcessor instance.

    Returns:
        Configured XbrzProcessor instance
    """
    return XbrzProcessor(scale=6)


@pytest.fixture
def potrace_processor() -> PotraceProcessor:
    """Pytest fixture that provides a PotraceProcessor instance.

    Returns:
        Configured PotraceProcessor instance
    """
    return PotraceProcessor(scale=10)


@pytest.mark.parametrize("input_filename", ["L", "RGB"])
def test_get_subs(input_filename: str):
    """Test NumPy crop boxes preserve full-image and partial-image pixels.

    Arguments:
        input_filename: input image filename
    """
    with Image.open(get_test_input_path(input_filename)) as image:
        boxes = np.array([[0, 0, *image.size], [3, 5, 13, 15]])
        subs = SubdividedImage.get_subs(image, boxes)
        image_array = np.array(image)

        assert len(subs) == 2
        assert all(sub.mode == image.mode for sub in subs)
        np.testing.assert_array_equal(np.array(subs[0]), image_array)
        np.testing.assert_array_equal(np.array(subs[1]), image_array[5:15, 3:13])


@pytest.mark.parametrize("mode", ["L", "RGB"])
@pytest.mark.parametrize("size", [(150, 50), (50, 150), (151, 57), (57, 151)])
@pytest.mark.parametrize("overlap", [0, 1, 10])
def test_recomposition_preserves_unchanged_subdivisions(
    mode: str, size: tuple[int, int], overlap: int
):
    """Test recomposition preserves pixels for short and odd tile dimensions.

    Arguments:
        mode: Image mode
        size: Image dimensions
        overlap: Overlap between tiles
    """
    channels = 1 if mode == "L" else 3
    array = np.arange(size[0] * size[1] * channels, dtype=np.uint8).reshape(
        (size[1], size[0]) if channels == 1 else (size[1], size[0], channels)
    )
    image = Image.fromarray(array, mode=mode)
    subdivided_image = SubdividedImage(image, 100, overlap)

    subdivided_image.subs = subdivided_image.subs

    np.testing.assert_array_equal(np.array(subdivided_image.image), array)


def test_subdivision_setter_preserves_integer_upscale():
    """Test subdivision assignment retains the supported integer upscale flow."""
    array = np.arange(150 * 250, dtype=np.uint8).reshape((150, 250))
    image = Image.fromarray(array, mode="L")
    subdivided_image = SubdividedImage(image, 100, 10)
    upscaled_subs = [
        sub.resize((sub.width * 2, sub.height * 2), Image.Resampling.NEAREST)
        for sub in subdivided_image.subs
    ]

    subdivided_image.subs = upscaled_subs

    assert subdivided_image.image.size == (500, 300)
    np.testing.assert_array_equal(
        np.array(subdivided_image.image),
        np.array(image.resize((500, 300), Image.Resampling.NEAREST)),
    )


def test_subdivision_setter_rejects_fractional_scale_without_mutating():
    """Test invalid fractional scaling leaves geometry and image unchanged."""
    subdivided_image = SubdividedImage(Image.new("L", (150, 50)), 100, 10)
    original_image = subdivided_image.image.copy()
    original_boxes = subdivided_image.boxes.copy()
    fractional_subs = [
        sub.resize((sub.width + sub.width // 2, sub.height + sub.height // 2))
        for sub in subdivided_image.subs
    ]

    with pytest.raises(ValueError, match="integer scale"):
        subdivided_image.subs = fractional_subs

    assert subdivided_image.image == original_image
    np.testing.assert_array_equal(subdivided_image.boxes, original_boxes)


def test_subdivision_setter_rejects_non_uniform_scale_without_mutating():
    """Test invalid non-uniform scaling leaves geometry and image unchanged."""
    subdivided_image = SubdividedImage(Image.new("L", (150, 50)), 100, 10)
    original_image = subdivided_image.image.copy()
    original_boxes = subdivided_image.boxes.copy()
    non_uniform_subs = [
        sub.resize((sub.width * 2, sub.height), Image.Resampling.NEAREST)
        for sub in subdivided_image.subs
    ]

    with pytest.raises(ValueError, match="uniform scale"):
        subdivided_image.subs = non_uniform_subs

    assert subdivided_image.image == original_image
    np.testing.assert_array_equal(subdivided_image.boxes, original_boxes)


@pytest.mark.parametrize("overlap", [-1, 100])
def test_subdivided_image_rejects_invalid_overlap(overlap: int):
    """Test overlap must be non-negative and smaller than subdivision size.

    Arguments:
        overlap: Invalid overlap value
    """
    with pytest.raises(ValueError):
        SubdividedImage(Image.new("L", (150, 50)), 100, overlap)


@pytest.mark.parametrize(
    ("processor_name", "input_filename", "scale"),
    [
        ("potrace_processor", "L", 10),
        ("xbrz_processor", "RGB", 6),
    ],
)
def test_subdivider(
    processor_name: str,
    input_filename: str,
    scale: int,
    request: pytest.FixtureRequest,
):
    """Test SubdividedImage processing images in subdivisions.

    Arguments:
        processor_name: Name of processor fixture to use
        input_filename: Input image filename
        scale: Expected output scale factor
        request: Pytest request fixture for accessing other fixtures
    """
    processor = request.getfixturevalue(processor_name)
    assert isinstance(processor, ImageProcessor)

    input_path = get_test_input_path(input_filename)
    input_img = Image.open(input_path)

    subdivided_img = SubdividedImage(input_img, 100, 10)
    subs = []
    for sub in subdivided_img.subs:
        img = processor(sub)
        subs.append(img)
    subdivided_img.subs = subs

    output_scale = subdivided_img.image.width / input_img.width
    assert output_scale == scale
