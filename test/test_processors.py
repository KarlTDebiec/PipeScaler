#!/usr/bin/env python
#   test_processors.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
from os.path import getsize

import numpy as np
import pytest
from PIL import Image
from shared import (
    esrgan_models,
    expected_output_mode,
    infiles,
    skip_if_ci,
    waifu_models,
    xfail_if_platform,
    xfail_unsupported_image_mode,
)

from pipescaler.common import temporary_filename
from pipescaler.processors import (
    AppleScriptExternalProcessor,
    AutomatorExternalProcessor,
    CropProcessor,
    ESRGANProcessor,
    ExpandProcessor,
    HeightToNormalProcessor,
    ModeProcessor,
    PngquantExternalProcessor,
    PotraceExternalProcessor,
    ResizeProcessor,
    SolidColorProcessor,
    TexconvExternalProcessor,
    ThresholdProcessor,
    WaifuExternalProcessor,
    WaifuProcessor,
    XbrzProcessor,
)

# region Fixtures


@pytest.fixture()
def apple_script_external_processor(request) -> AppleScriptExternalProcessor:
    return AppleScriptExternalProcessor(**request.param)


@pytest.fixture()
def automator_external_processor(request) -> AutomatorExternalProcessor:
    return AutomatorExternalProcessor(**request.param)


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
def pngquant_external_processor(request) -> PngquantExternalProcessor:
    return PngquantExternalProcessor(**request.param)


@pytest.fixture()
def resize_processor(request) -> ResizeProcessor:
    return ResizeProcessor(**request.param)


@pytest.fixture()
def solid_color_processor(request) -> SolidColorProcessor:
    return SolidColorProcessor(**request.param)


@pytest.fixture()
def texconv_external_processor(request) -> TexconvExternalProcessor:
    return TexconvExternalProcessor(**request.param)


@pytest.fixture()
def threshold_processor(request) -> ThresholdProcessor:
    return ThresholdProcessor(**request.param)


@pytest.fixture()
def waifu_external_processor(request) -> WaifuExternalProcessor:
    return WaifuExternalProcessor(**request.param)


@pytest.fixture()
def waifu_processor(request) -> WaifuProcessor:
    return WaifuProcessor(**request.param)


@pytest.fixture()
def xbrz_processor(request) -> XbrzProcessor:
    return XbrzProcessor(**request.param)


# endregion


@pytest.mark.serial
@pytest.mark.parametrize(
    ("infile", "apple_script_external_processor"),
    [
        xfail_if_platform({"Linux", "Windows"})(
            infiles["RGB"],
            {"script": "pixelmator/ml_super_resolution.scpt", "args": "2"},
        ),
        xfail_if_platform({"Linux", "Windows"})(
            infiles["RGBA"],
            {"script": "pixelmator/ml_super_resolution.scpt", "args": "2"},
        ),
    ],
    indirect=["apple_script_external_processor"],
)
def test_apple_script_external(
    infile: str, apple_script_external_processor: AppleScriptExternalProcessor
) -> None:
    with temporary_filename(".png") as outfile:
        apple_script_external_processor(infile, outfile)

        with Image.open(infile) as input_image, Image.open(outfile) as output_image:
            assert output_image.mode == input_image.mode
            assert output_image.size == (
                input_image.size[0] * int(apple_script_external_processor.args),
                input_image.size[1] * int(apple_script_external_processor.args),
            )


@pytest.mark.serial
@pytest.mark.parametrize(
    ("infile", "automator_external_processor"),
    [
        xfail_if_platform({"Linux", "Windows"})(
            infiles["RGB"],
            {"workflow": "pixelmator/denoise.workflow"},
        ),
        xfail_if_platform({"Linux", "Windows"})(
            infiles["RGBA"],
            {"workflow": "pixelmator/denoise.workflow"},
        ),
    ],
    indirect=["automator_external_processor"],
)
def test_automator_external(
    infile: str, automator_external_processor: AutomatorExternalProcessor
) -> None:
    with temporary_filename(".png") as outfile:
        automator_external_processor(infile, outfile)

        with Image.open(infile) as input_image, Image.open(outfile) as output_image:
            assert output_image.mode == input_image.mode
            assert output_image.size == input_image.size


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
@pytest.mark.parametrize(
    ("infile", "esrgan_processor"),
    [
        skip_if_ci()(infiles["L"], {"model_infile": esrgan_models["1x_BC1-smooth2"]}),
        skip_if_ci()(infiles["PL"], {"model_infile": esrgan_models["1x_BC1-smooth2"]}),
        skip_if_ci()(
            infiles["PRGB"], {"model_infile": esrgan_models["1x_BC1-smooth2"]}
        ),
        skip_if_ci()(infiles["RGB"], {"model_infile": esrgan_models["1x_BC1-smooth2"]}),
        skip_if_ci()(infiles["RGB"], {"model_infile": esrgan_models["RRDB_ESRGAN_x4"]}),
        skip_if_ci()(
            infiles["RGB"], {"model_infile": esrgan_models["RRDB_ESRGAN_x4_old_arch"]}
        ),
        skip_if_ci(xfail_unsupported_image_mode())(
            infiles["LA"], {"model_infile": esrgan_models["1x_BC1-smooth2"]}
        ),
        skip_if_ci(xfail_unsupported_image_mode())(
            infiles["PLA"], {"model_infile": esrgan_models["1x_BC1-smooth2"]}
        ),
        skip_if_ci(xfail_unsupported_image_mode())(
            infiles["PRGBA"], {"model_infile": esrgan_models["1x_BC1-smooth2"]}
        ),
        skip_if_ci(xfail_unsupported_image_mode())(
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
        xfail_unsupported_image_mode()(infiles["LA"], {"sigma": 1.0}),
        (infiles["PL"], {"sigma": 1.0}),
        xfail_unsupported_image_mode()(infiles["PLA"], {"sigma": 1.0}),
        xfail_unsupported_image_mode()(infiles["PRGB"], {"sigma": 1.0}),
        xfail_unsupported_image_mode()(infiles["PRGBA"], {"sigma": 1.0}),
        xfail_unsupported_image_mode()(infiles["RGB"], {"sigma": 1.0}),
        xfail_unsupported_image_mode()(infiles["RGBA"], {"sigma": 1.0}),
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
        (infiles["1"], {"mode": "1"}),
        (infiles["1"], {"mode": "L"}),
        (infiles["1"], {"mode": "LA"}),
        (infiles["1"], {"mode": "RGB"}),
        (infiles["1"], {"mode": "RGBA"}),
        (infiles["L"], {"mode": "1"}),
        (infiles["L"], {"mode": "L"}),
        (infiles["L"], {"mode": "LA"}),
        (infiles["L"], {"mode": "RGB"}),
        (infiles["L"], {"mode": "RGBA"}),
        (infiles["LA"], {"mode": "1"}),
        (infiles["LA"], {"mode": "L"}),
        (infiles["LA"], {"mode": "LA"}),
        (infiles["LA"], {"mode": "RGB"}),
        (infiles["LA"], {"mode": "RGBA"}),
        (infiles["RGB"], {"mode": "1"}),
        (infiles["RGB"], {"mode": "L"}),
        (infiles["RGB"], {"mode": "LA"}),
        (infiles["RGB"], {"mode": "RGB"}),
        (infiles["RGB"], {"mode": "RGBA"}),
        (infiles["RGBA"], {"mode": "1"}),
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


@pytest.mark.parametrize(
    ("infile", "pngquant_external_processor"),
    [
        (infiles["L"], {}),
        (infiles["LA"], {}),
        (infiles["RGB"], {}),
        (infiles["RGBA"], {}),
        (infiles["PL"], {}),
        (infiles["PRGB"], {}),
        (infiles["PRGBA"], {}),
        (infiles["PLA"], {}),
    ],
    indirect=["pngquant_external_processor"],
)
def test_pngquant_external(
    infile: str, pngquant_external_processor: PngquantExternalProcessor
) -> None:
    with temporary_filename(".png") as outfile:
        pngquant_external_processor(infile, outfile)

        with Image.open(infile) as input_image, Image.open(outfile) as output_image:
            assert output_image.mode in (input_image.mode, "P")
            assert output_image.size == input_image.size
            assert getsize(outfile) <= getsize(infile)


@pytest.mark.parametrize(
    ("infile", "potrace_external_processor"),
    [
        (infiles["L"], {}),
        (infiles["L"], {"scale": 2}),
        xfail_unsupported_image_mode()(infiles["LA"], {}),
        (infiles["PL"], {}),
        xfail_unsupported_image_mode()(infiles["PLA"], {}),
        xfail_unsupported_image_mode()(infiles["PRGB"], {}),
        xfail_unsupported_image_mode()(infiles["PRGBA"], {}),
        xfail_unsupported_image_mode()(infiles["RGB"], {}),
        xfail_unsupported_image_mode()(infiles["RGBA"], {}),
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


@pytest.mark.parametrize(
    ("infile", "texconv_external_processor"),
    [
        xfail_if_platform({"Darwin", "Linux"})(infiles["L"], {}),
        xfail_if_platform({"Darwin", "Linux"})(infiles["LA"], {}),
        xfail_if_platform({"Darwin", "Linux"})(infiles["RGB"], {}),
        xfail_if_platform({"Darwin", "Linux"})(infiles["RGBA"], {}),
        xfail_if_platform({"Darwin", "Linux"})(infiles["PL"], {}),
        xfail_if_platform({"Darwin", "Linux"})(infiles["PLA"], {}),
        xfail_if_platform({"Darwin", "Linux"})(infiles["PRGB"], {}),
        xfail_if_platform({"Darwin", "Linux"})(infiles["PRGBA"], {}),
    ],
    indirect=["texconv_external_processor"],
)
def test_texconv_external(
    infile: str, texconv_external_processor: TexconvExternalProcessor
) -> None:
    with temporary_filename(".png") as outfile:
        texconv_external_processor(infile, outfile)

        with Image.open(infile) as input_image, Image.open(outfile) as output_image:
            assert output_image.mode == "RGBA"
            assert output_image.size == input_image.size


@pytest.mark.parametrize(
    ("infile", "threshold_processor"),
    [
        (infiles["L"], {}),
        (infiles["L"], {"denoise": True}),
        xfail_unsupported_image_mode()(infiles["LA"], {}),
        (infiles["PL"], {}),
        xfail_unsupported_image_mode()(infiles["PLA"], {}),
        xfail_unsupported_image_mode()(infiles["PRGB"], {}),
        xfail_unsupported_image_mode()(infiles["PRGBA"], {}),
        xfail_unsupported_image_mode()(infiles["RGB"], {}),
        xfail_unsupported_image_mode()(infiles["RGBA"], {}),
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
@pytest.mark.parametrize(
    ("infile", "scale", "waifu_processor"),
    [
        skip_if_ci()(
            infiles["L"], 2, {"model_infile": waifu_models["WaifuUpConv7/a-2-3"]}
        ),
        skip_if_ci()(
            infiles["L"], 1, {"model_infile": waifu_models["WaifuVgg7/a-1-3"]}
        ),
        skip_if_ci(xfail_unsupported_image_mode())(
            infiles["LA"], 2, {"model_infile": waifu_models["WaifuUpConv7/a-2-3"]}
        ),
        skip_if_ci()(
            infiles["RGB"], 2, {"model_infile": waifu_models["WaifuUpConv7/a-2-3"]}
        ),
        skip_if_ci()(
            infiles["RGB"], 1, {"model_infile": waifu_models["WaifuVgg7/a-1-3"]}
        ),
        skip_if_ci(xfail_unsupported_image_mode())(
            infiles["RGBA"], 2, {"model_infile": waifu_models["WaifuUpConv7/a-2-3"]}
        ),
    ],
    indirect=["waifu_processor"],
)
def test_waifu(infile: str, scale: int, waifu_processor: WaifuProcessor) -> None:
    with temporary_filename(".png") as outfile:
        waifu_processor(infile, outfile)

        with Image.open(infile) as input_image, Image.open(outfile) as output_image:
            assert output_image.mode == expected_output_mode(input_image)
            assert output_image.size == (
                input_image.size[0] * scale,
                input_image.size[1] * scale,
            )


@pytest.mark.serial
@pytest.mark.parametrize(
    ("infile", "waifu_external_processor"),
    [
        skip_if_ci()(infiles["L"], {"imagetype": "a", "denoise": 0, "scale": 2}),
        skip_if_ci()(infiles["PL"], {"imagetype": "a", "denoise": 0, "scale": 2}),
        skip_if_ci()(infiles["PRGB"], {"imagetype": "a", "denoise": 0, "scale": 2}),
        skip_if_ci()(infiles["RGB"], {"imagetype": "a", "denoise": 0, "scale": 2}),
        skip_if_ci()(infiles["RGB"], {"imagetype": "a", "denoise": 3, "scale": 2}),
        skip_if_ci(xfail_unsupported_image_mode())(
            infiles["LA"], {"imagetype": "a", "denoise": 0, "scale": 2}
        ),
        skip_if_ci(xfail_unsupported_image_mode())(
            infiles["PLA"], {"imagetype": "a", "denoise": 0, "scale": 2}
        ),
        skip_if_ci(xfail_unsupported_image_mode())(
            infiles["PRGBA"], {"imagetype": "a", "denoise": 0, "scale": 2}
        ),
        skip_if_ci(xfail_unsupported_image_mode())(
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
