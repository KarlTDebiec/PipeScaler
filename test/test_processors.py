#!/usr/bin/env python
#   test_processors.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
""""""
from os import getenv
from os.path import getsize
from platform import win32_ver

import numpy as np
import pytest
from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.core import UnsupportedPlatformError
from pipescaler.processors import (
    CropProcessor,
    ESRGANProcessor,
    ExpandProcessor,
    HeightToNormalProcessor,
    ModeProcessor,
    PngquantExternalProcessor,
    PotraceExternalProcessor,
    ResizeProcessor,
    SolidColorProcessor,
    TexconvProcessor,
    ThresholdProcessor,
    WaifuExternalProcessor,
    WaifuProcessor,
    XbrzProcessor,
)

# noinspection PyUnresolvedReferences
from shared import (
    esrgan_models,
    expected_output_mode,
    infiles,
    skip_if_ci,
    xfail_if_not_windows,
    xfail_unsupported_mode,
)


@pytest.fixture()
def crop_processor(request) -> CropProcessor:
    return CropProcessor(**request.param)


@pytest.fixture()
def esrgan_processor(request) -> ESRGANProcessor:
    return ESRGANProcessor(**request.param)


@pytest.fixture()
def expand_processor(request) -> ExpandProcessor:
    return ExpandProcessor(**request.param)


@pytest.fixture()
def height_to_normal_processor(request) -> HeightToNormalProcessor:
    return HeightToNormalProcessor(**request.param)


@pytest.fixture()
def mode_processor(request) -> ModeProcessor:
    return ModeProcessor(**request.param)


@pytest.fixture()
def potrace_external_processor(request) -> PotraceExternalProcessor:
    return PotraceExternalProcessor(**request.param)


@pytest.fixture()
def pngquant_processor(request) -> PngquantExternalProcessor:
    return PngquantExternalProcessor(**request.param)


@pytest.fixture()
def resize_processor(request) -> ResizeProcessor:
    return ResizeProcessor(**request.param)


@pytest.fixture()
def solid_color_processor(request) -> SolidColorProcessor:
    return SolidColorProcessor(**request.param)


@pytest.fixture()
def texconv_processor(request) -> TexconvProcessor:
    return TexconvProcessor(**request.param)


@pytest.fixture()
def threshold_processor(request) -> ThresholdProcessor:
    return ThresholdProcessor(**request.param)


@pytest.fixture()
def waifu_processor(request) -> WaifuProcessor:
    return WaifuProcessor(**request.param)


@pytest.fixture()
def waifu_external_processor(request) -> WaifuExternalProcessor:
    return WaifuExternalProcessor(**request.param)


@pytest.fixture()
def xbrz_processor(request) -> XbrzProcessor:
    return XbrzProcessor(**request.param)


@pytest.mark.parametrize(
    ("infile", "crop_processor"),
    [
        (infiles["L"], {"pixels": (4, 4, 4, 4)}),
        (infiles["LA"], {"pixels": (4, 4, 4, 4)}),
        (infiles["RGB"], {"pixels": (4, 4, 4, 4)}),
        (infiles["RGBA"], {"pixels": (4, 4, 4, 4)}),
        (infiles["PL"], {"pixels": (4, 4, 4, 4)}),
        (infiles["PLA"], {"pixels": (4, 4, 4, 4)}),
        (infiles["PRGB"], {"pixels": (4, 4, 4, 4)}),
        (infiles["PRGBA"], {"pixels": (4, 4, 4, 4)}),
    ],
    indirect=["crop_processor"],
)
def test_crop(infile: str, crop_processor: CropProcessor) -> None:
    with temporary_filename(".png") as outfile:
        crop_processor(infile, outfile)

        with Image.open(infile) as input_image, Image.open(outfile) as output_image:
            assert output_image.mode == input_image.mode
            assert output_image.size == (
                input_image.size[0] - crop_processor.left - crop_processor.right,
                input_image.size[1] - crop_processor.top - crop_processor.bottom,
            )


@pytest.mark.serial
@pytest.mark.skipif(
    getenv("CONTINUOUS_INTEGRATION") is not None, reason="Skip when running in CI"
)
@pytest.mark.parametrize(
    ("infile", "esrgan_processor"),
    [
        (infiles["L"], {"model_infile": esrgan_models["1x_BC1-smooth2"]}),
        (infiles["PL"], {"model_infile": esrgan_models["1x_BC1-smooth2"]}),
        (infiles["PRGB"], {"model_infile": esrgan_models["1x_BC1-smooth2"]}),
        (infiles["RGB"], {"model_infile": esrgan_models["1x_BC1-smooth2"]}),
        (infiles["RGB"], {"model_infile": esrgan_models["RRDB_ESRGAN_x4"]}),
        (infiles["RGB"], {"model_infile": esrgan_models["RRDB_ESRGAN_x4_old_arch"]}),
        xfail_unsupported_mode(
            infiles["LA"], {"model_infile": esrgan_models["1x_BC1-smooth2"]}
        ),
        xfail_unsupported_mode(
            infiles["PLA"], {"model_infile": esrgan_models["1x_BC1-smooth2"]}
        ),
        xfail_unsupported_mode(
            infiles["PRGBA"], {"model_infile": esrgan_models["1x_BC1-smooth2"]}
        ),
        xfail_unsupported_mode(
            infiles["RGBA"], {"model_infile": esrgan_models["1x_BC1-smooth2"]}
        ),
    ],
    indirect=["esrgan_processor"],
)
def test_esrgan(infile: str, esrgan_processor: ESRGANProcessor) -> None:
    with temporary_filename(".png") as outfile:
        esrgan_processor(infile, outfile)

        with Image.open(infile) as input_image, Image.open(outfile) as output_image:
            assert output_image.mode == expected_output_mode(input_image)


@pytest.mark.parametrize(
    ("infile", "expand_processor"),
    [
        (infiles["L"], {"pixels": (4, 4, 4, 4)}),
        (infiles["LA"], {"pixels": (4, 4, 4, 4)}),
        (infiles["RGB"], {"pixels": (4, 4, 4, 4)}),
        (infiles["RGBA"], {"pixels": (4, 4, 4, 4)}),
        (infiles["PL"], {"pixels": (4, 4, 4, 4)}),
        (infiles["PLA"], {"pixels": (4, 4, 4, 4)}),
        (infiles["PRGB"], {"pixels": (4, 4, 4, 4)}),
        (infiles["PRGBA"], {"pixels": (4, 4, 4, 4)}),
    ],
    indirect=["expand_processor"],
)
def test_expand(infile: str, expand_processor: ExpandProcessor) -> None:
    with temporary_filename(".png") as outfile:
        expand_processor(infile, outfile)

        with Image.open(infile) as input_image, Image.open(outfile) as output_image:
            assert output_image.mode == input_image.mode
            assert output_image.size == (
                input_image.size[0] + expand_processor.left + expand_processor.right,
                input_image.size[1] + expand_processor.top + expand_processor.bottom,
            )


@pytest.mark.parametrize(
    ("infile", "height_to_normal_processor"),
    [
        (infiles["L"], {"sigma": 0.5}),
        (infiles["L"], {"sigma": 1.0}),
        xfail_unsupported_mode(infiles["LA"], {"sigma": 1.0}),
        (infiles["PL"], {"sigma": 1.0}),
        xfail_unsupported_mode(infiles["PLA"], {"sigma": 1.0}),
        xfail_unsupported_mode(infiles["PRGB"], {"sigma": 1.0}),
        xfail_unsupported_mode(infiles["PRGBA"], {"sigma": 1.0}),
        xfail_unsupported_mode(infiles["RGB"], {"sigma": 1.0}),
        xfail_unsupported_mode(infiles["RGBA"], {"sigma": 1.0}),
    ],
    indirect=["height_to_normal_processor"],
)
def test_height_to_normal(
    infile: str, height_to_normal_processor: HeightToNormalProcessor
) -> None:
    with temporary_filename(".png") as outfile:
        height_to_normal_processor(infile, outfile)

        with Image.open(infile) as input_image, Image.open(outfile) as output_image:
            output_datum = np.array(output_image)
            assert output_image.mode == "RGB"
            assert output_image.size == input_image.size
            assert np.min(output_datum[:, :, 2] >= 128)


@pytest.mark.parametrize(
    ("infile", "mode_processor"),
    [
        (infiles["L"], {"mode": "L"}),
        (infiles["L"], {"mode": "LA"}),
        (infiles["L"], {"mode": "RGB"}),
        (infiles["L"], {"mode": "RGBA"}),
        (infiles["LA"], {"mode": "L"}),
        (infiles["LA"], {"mode": "LA"}),
        (infiles["LA"], {"mode": "RGB"}),
        (infiles["LA"], {"mode": "RGBA"}),
        (infiles["RGB"], {"mode": "L"}),
        (infiles["RGB"], {"mode": "LA"}),
        (infiles["RGB"], {"mode": "RGB"}),
        (infiles["RGB"], {"mode": "RGBA"}),
        (infiles["RGBA"], {"mode": "L"}),
        (infiles["RGBA"], {"mode": "LA"}),
        (infiles["RGBA"], {"mode": "RGB"}),
        (infiles["RGBA"], {"mode": "RGBA"}),
        (infiles["PL"], {"mode": "RGBA"}),
        (infiles["PLA"], {"mode": "RGBA"}),
        (infiles["PRGB"], {"mode": "RGBA"}),
        (infiles["PRGBA"], {"mode": "RGBA"}),
    ],
    indirect=["mode_processor"],
)
def test_mode(infile: str, mode_processor: ModeProcessor) -> None:
    with temporary_filename(".png") as outfile:
        mode_processor(infile, outfile)

        with Image.open(infile) as input_image, Image.open(outfile) as output_image:
            assert output_image.size == input_image.size
            assert output_image.mode == mode_processor.mode


@pytest.mark.skipif(
    getenv("CONTINUOUS_INTEGRATION") is not None, reason="Skip when running in CI"
)
@pytest.mark.parametrize(
    ("infile", "pngquant_processor"),
    [
        (infiles["L"], {}),
        (infiles["LA"], {}),
        (infiles["RGB"], {}),
        (infiles["RGBA"], {}),
        (infiles["PL"], {}),
        (infiles["PLA"], {}),
        (infiles["PRGB"], {}),
        (infiles["PRGBA"], {}),
    ],
    indirect=["pngquant_processor"],
)
def test_pngquant(infile: str, pngquant_processor: PngquantExternalProcessor) -> None:
    with temporary_filename(".png") as outfile:
        pngquant_processor(infile, outfile)

        with Image.open(infile) as input_image, Image.open(outfile) as output_image:
            assert output_image.mode in (input_image.mode, "P")
            assert output_image.size == input_image.size
            assert getsize(outfile) <= getsize(infile)


@pytest.mark.parametrize(
    ("infile", "potrace_external_processor"),
    [
        (infiles["L"], {}),
        (infiles["L"], {"scale": 2}),
        xfail_unsupported_mode(infiles["LA"], {}),
        (infiles["PL"], {}),
        xfail_unsupported_mode(infiles["PLA"], {}),
        xfail_unsupported_mode(infiles["PRGB"], {}),
        xfail_unsupported_mode(infiles["PRGBA"], {}),
        xfail_unsupported_mode(infiles["RGB"], {}),
        xfail_unsupported_mode(infiles["RGBA"], {}),
    ],
    indirect=["potrace_external_processor"],
)
def test_potrace_external(
    infile: str, potrace_external_processor: PotraceExternalProcessor
) -> None:
    with temporary_filename(".png") as outfile:
        potrace_external_processor(infile, outfile)

        with Image.open(infile) as input_image, Image.open(outfile) as output_image:
            assert output_image.mode == "L"
            assert output_image.size == (
                input_image.size[0] * potrace_external_processor.scale,
                input_image.size[1] * potrace_external_processor.scale,
            )


@pytest.mark.parametrize(
    ("infile", "resize_processor"),
    [
        (infiles["L"], {"scale": 2}),
        (infiles["LA"], {"scale": 2}),
        (infiles["RGB"], {"scale": 2}),
        (infiles["RGBA"], {"scale": 2}),
        (infiles["PL"], {"scale": 2}),
        (infiles["PLA"], {"scale": 2}),
        (infiles["PRGB"], {"scale": 2}),
        (infiles["PRGBA"], {"scale": 2}),
    ],
    indirect=["resize_processor"],
)
def test_resize(infile: str, resize_processor: ResizeProcessor) -> None:
    with temporary_filename(".png") as outfile:
        resize_processor(infile, outfile)

        with Image.open(infile) as input_image, Image.open(outfile) as output_image:
            assert output_image.mode == expected_output_mode(input_image)
            assert output_image.size == (
                input_image.size[0] * resize_processor.scale,
                input_image.size[1] * resize_processor.scale,
            )


@pytest.mark.parametrize(
    ("infile", "solid_color_processor"),
    [
        (infiles["L"], {}),
        (infiles["LA"], {}),
        (infiles["RGB"], {}),
        (infiles["RGBA"], {}),
        (infiles["PL"], {}),
        (infiles["PLA"], {}),
        (infiles["PRGB"], {}),
        (infiles["PRGBA"], {}),
    ],
    indirect=["solid_color_processor"],
)
def test_solid_color(infile: str, solid_color_processor: SolidColorProcessor) -> None:
    with temporary_filename(".png") as outfile:
        solid_color_processor(infile, outfile)

        with Image.open(infile) as input_image, Image.open(outfile) as output_image:
            assert output_image.mode == expected_output_mode(input_image)
            assert output_image.size == input_image.size
            assert len(output_image.getcolors()) == 1


@pytest.mark.skipif(
    getenv("CONTINUOUS_INTEGRATION") is not None, reason="Skip when running in CI"
)
@pytest.mark.xfail(
    not any(win32_ver()),
    raises=UnsupportedPlatformError,
    reason="Only supported on Windows",
)
@pytest.mark.parametrize(
    ("infile", "texconv_processor"),
    [
        (infiles["L"], {}),
        (infiles["LA"], {}),
        (infiles["RGB"], {}),
        (infiles["RGBA"], {}),
        (infiles["PL"], {}),
        (infiles["PLA"], {}),
        (infiles["PRGB"], {}),
        (infiles["PRGBA"], {}),
    ],
    indirect=["texconv_processor"],
)
def test_texconv(infile: str, texconv_processor: TexconvProcessor) -> None:
    with temporary_filename(".png") as outfile:
        texconv_processor(infile, outfile)

        with Image.open(infile) as input_image, Image.open(outfile) as output_image:
            assert output_image.mode == "RGBA"
            assert output_image.size == input_image.size


@pytest.mark.parametrize(
    ("infile", "threshold_processor"),
    [
        (infiles["L"], {}),
        (infiles["L"], {"denoise": True}),
        xfail_unsupported_mode(infiles["LA"], {}),
        (infiles["PL"], {}),
        xfail_unsupported_mode(infiles["PLA"], {}),
        xfail_unsupported_mode(infiles["PRGB"], {}),
        xfail_unsupported_mode(infiles["PRGBA"], {}),
        xfail_unsupported_mode(infiles["RGB"], {}),
        xfail_unsupported_mode(infiles["RGBA"], {}),
    ],
    indirect=["threshold_processor"],
)
def test_threshold(infile: str, threshold_processor: ThresholdProcessor) -> None:
    with temporary_filename(".png") as outfile:
        threshold_processor(infile, outfile)

        with Image.open(infile) as input_image, Image.open(outfile) as output_image:
            output_datum = np.array(output_image)
            assert output_image.mode == "L"
            assert output_image.size == input_image.size
            assert np.logical_or(output_datum == 0, output_datum == 255).all()


@pytest.mark.serial
@pytest.mark.skipif(
    getenv("CONTINUOUS_INTEGRATION") is not None, reason="Skip when running in CI"
)
@pytest.mark.parametrize(
    ("infile", "waifu_processor"),
    [
        (infiles["L"], {"architecture": "resnet10", "denoise": 0, "scale": 2}),
        (infiles["PL"], {"architecture": "resnet10", "denoise": 0, "scale": 2}),
        (infiles["PRGB"], {"architecture": "resnet10", "denoise": 0, "scale": 2}),
        (infiles["RGB"], {"architecture": "resnet10", "denoise": 0, "scale": 2}),
        (infiles["RGB"], {"architecture": "upconv7", "denoise": 0, "scale": 2}),
        (infiles["RGB"], {"architecture": "upresnet10", "denoise": 0, "scale": 2}),
        (infiles["RGB"], {"architecture": "vgg7", "denoise": 0, "scale": 2}),
        (infiles["RGB"], {"architecture": "resnet10", "denoise": 0, "scale": 1}),
        (infiles["RGB"], {"architecture": "upconv7", "denoise": 1, "scale": 2}),
        (infiles["RGB"], {"architecture": "upresnet10", "denoise": 2, "scale": 2}),
        (infiles["RGB"], {"architecture": "vgg7", "denoise": 3, "scale": 2}),
        xfail_unsupported_mode(
            infiles["LA"], {"architecture": "resnet10", "denoise": 0, "scale": 2}
        ),
        xfail_unsupported_mode(
            infiles["PLA"], {"architecture": "resnet10", "denoise": 0, "scale": 2}
        ),
        xfail_unsupported_mode(
            infiles["PRGBA"], {"architecture": "resnet10", "denoise": 0, "scale": 2}
        ),
        xfail_unsupported_mode(
            infiles["RGBA"], {"architecture": "resnet10", "denoise": 0, "scale": 2}
        ),
    ],
    indirect=["waifu_processor"],
)
def test_waifu(infile: str, waifu_processor: WaifuProcessor) -> None:
    with temporary_filename(".png") as outfile:
        waifu_processor(infile, outfile)

        with Image.open(infile) as input_image, Image.open(outfile) as output_image:
            assert output_image.mode == expected_output_mode(input_image)
            assert output_image.size == (
                input_image.size[0] * waifu_processor.scale,
                input_image.size[1] * waifu_processor.scale,
            )


@pytest.mark.serial
@pytest.mark.skipif(
    getenv("CONTINUOUS_INTEGRATION") is not None, reason="Skip when running in CI"
)
@pytest.mark.parametrize(
    ("infile", "waifu_external_processor"),
    [
        (infiles["L"], {"imagetype": "a", "denoise": 0, "scale": 2}),
        (infiles["PL"], {"imagetype": "a", "denoise": 0, "scale": 2}),
        (infiles["PRGB"], {"imagetype": "a", "denoise": 0, "scale": 2}),
        (infiles["RGB"], {"imagetype": "a", "denoise": 0, "scale": 2}),
        (infiles["RGB"], {"imagetype": "a", "denoise": 3, "scale": 2}),
        xfail_unsupported_mode(
            infiles["LA"], {"imagetype": "a", "denoise": 0, "scale": 2}
        ),
        xfail_unsupported_mode(
            infiles["PLA"], {"imagetype": "a", "denoise": 0, "scale": 2}
        ),
        xfail_unsupported_mode(
            infiles["PRGBA"], {"imagetype": "a", "denoise": 0, "scale": 2}
        ),
        xfail_unsupported_mode(
            infiles["RGBA"], {"imagetype": "a", "denoise": 0, "scale": 2}
        ),
    ],
    indirect=["waifu_external_processor"],
)
def test_waifu_external(
    infile: str, waifu_external_processor: WaifuExternalProcessor
) -> None:
    with temporary_filename(".png") as outfile:
        waifu_external_processor(infile, outfile)

        with Image.open(infile) as input_image, Image.open(outfile) as output_image:
            assert output_image.mode == expected_output_mode(input_image)
            assert output_image.size == (
                input_image.size[0] * waifu_external_processor.scale,
                input_image.size[1] * waifu_external_processor.scale,
            )


@pytest.mark.parametrize(
    ("infile", "xbrz_processor"),
    [
        (infiles["L"], {"scale": 2}),
        (infiles["LA"], {"scale": 2}),
        (infiles["RGB"], {"scale": 2}),
        (infiles["RGBA"], {"scale": 2}),
        (infiles["PL"], {"scale": 2}),
        (infiles["PLA"], {"scale": 2}),
        (infiles["PRGB"], {"scale": 2}),
        (infiles["PRGBA"], {"scale": 2}),
    ],
    indirect=["xbrz_processor"],
)
def test_xbrz(infile: str, xbrz_processor: XbrzProcessor) -> None:
    with temporary_filename(".png") as outfile:
        xbrz_processor(infile, outfile)

        with Image.open(infile) as input_image, Image.open(outfile) as output_image:
            assert output_image.mode == expected_output_mode(input_image)
            assert output_image.size == (
                input_image.size[0] * xbrz_processor.scale,
                input_image.size[1] * xbrz_processor.scale,
            )
