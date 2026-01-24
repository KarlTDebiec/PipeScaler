#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for SubdividedImage."""

import pytest
from PIL import Image

from pipescaler.image import SubdividedImage
from pipescaler.image.core.operators import ImageProcessor
from pipescaler.image.operators.processors import (
    EsrganProcessor,
    PotraceProcessor,
    WaifuProcessor,
    XbrzProcessor,
)
from pipescaler.image.testing import xfail_unsupported_image_mode
from pipescaler.testing.file import get_test_input_path, get_test_model_path
from pipescaler.testing.mark import skip_if_ci, skip_if_codex


@pytest.fixture
def esrgan_bc1s2_processor(request) -> EsrganProcessor:
    """Pytest fixture that provides an EsrganProcessor with BC1-smooth2 model.

    Arguments:
        request: Pytest request fixture
    Returns:
        Configured EsrganProcessor instance
    """
    return EsrganProcessor(
        model_input_path=get_test_model_path("ESRGAN/1x_BC1-smooth2")
    )


@pytest.fixture
def esrgan_rrdb_processor() -> EsrganProcessor:
    """Pytest fixture that provides an EsrganProcessor with RRDB_ESRGAN_x4 model.

    Returns:
        Configured EsrganProcessor instance
    """
    return EsrganProcessor(
        model_input_path=get_test_model_path("ESRGAN/RRDB_ESRGAN_x4")
    )


@pytest.fixture
def waifu_processor() -> WaifuProcessor:
    """Pytest fixture that provides a WaifuProcessor instance.

    Returns:
        Configured WaifuProcessor instance
    """
    return WaifuProcessor(model_input_path=get_test_model_path("WaifuUpConv7/a-2-3"))


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


@pytest.mark.parametrize(
    ("processor_name", "input_filename", "scale"),
    [
        skip_if_codex(skip_if_ci())("esrgan_bc1s2_processor", "L", 1),
        skip_if_codex(skip_if_ci())("esrgan_bc1s2_processor", "RGB", 1),
        skip_if_codex(skip_if_ci(xfail_unsupported_image_mode()))(
            "esrgan_bc1s2_processor", "RGBA", 1
        ),
        skip_if_codex(skip_if_ci())("esrgan_rrdb_processor", "RGB", 4),
        ("potrace_processor", "L", 10),
        skip_if_codex(skip_if_ci())("waifu_processor", "RGB", 2),
        ("xbrz_processor", "RGB", 6),
    ],
)
def test_subdivider(processor_name: str, input_filename: str, scale: int, request):
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
