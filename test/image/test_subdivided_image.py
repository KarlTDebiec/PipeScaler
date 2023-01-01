#  Copyright 2020-2023 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Tests for SubdividedImage."""
import pytest
from PIL import Image

from pipescaler.image import SubdividedImage, xfail_unsupported_image_mode
from pipescaler.image.core.operators import ImageProcessor
from pipescaler.image.operators.processors import (
    EsrganProcessor,
    PotraceProcessor,
    WaifuProcessor,
    XbrzProcessor,
)
from pipescaler.testing import (
    get_test_infile_path,
    get_test_model_infile_path,
    skip_if_ci,
)


@pytest.fixture
def esrgan_bc1s2_processor(request) -> EsrganProcessor:
    return EsrganProcessor(
        model_infile=get_test_model_infile_path("ESRGAN/1x_BC1-smooth2")
    )


@pytest.fixture
def esrgan_rrdb_processor() -> EsrganProcessor:
    return EsrganProcessor(
        model_infile=get_test_model_infile_path("ESRGAN/RRDB_ESRGAN_x4")
    )


@pytest.fixture
def waifu_processor() -> WaifuProcessor:
    return WaifuProcessor(model_infile=get_test_model_infile_path("WaifuUpConv7/a-2-3"))


@pytest.fixture
def xbrz_processor() -> XbrzProcessor:
    return XbrzProcessor(scale=6)


@pytest.fixture
def potrace_processor() -> PotraceProcessor:
    return PotraceProcessor(scale=10)


@pytest.mark.parametrize(
    ("processor_name", "infile", "scale"),
    [
        skip_if_ci()("esrgan_bc1s2_processor", "L", 1),
        skip_if_ci()("esrgan_bc1s2_processor", "RGB", 1),
        skip_if_ci(xfail_unsupported_image_mode())("esrgan_bc1s2_processor", "RGBA", 1),
        skip_if_ci()("esrgan_rrdb_processor", "RGB", 4),
        ("potrace_processor", "L", 10),
        skip_if_ci()("waifu_processor", "RGB", 2),
        ("xbrz_processor", "RGB", 6),
    ],
)
def test_subdivider(processor_name: str, infile: str, scale: int, request) -> None:
    processor = request.getfixturevalue(processor_name)
    assert isinstance(processor, ImageProcessor)

    input_path = get_test_infile_path(infile)
    input_image = Image.open(input_path)

    subdivided_image = SubdividedImage(input_image, 100, 10)
    subs = []
    for sub in subdivided_image.subs:
        image = processor(sub)
        subs.append(image)
    subdivided_image.subs = subs

    output_scale = subdivided_image.image.width / input_image.width
    assert output_scale == scale
