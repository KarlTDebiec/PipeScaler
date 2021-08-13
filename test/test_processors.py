#!/usr/bin/env python
#   test_processors.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
####################################### MODULES ########################################
from inspect import getfile
from os import getcwd
from os.path import getsize, join
from platform import win32_ver
from subprocess import Popen

import pytest
from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.core import Processor
from pipescaler.processors import (
    AppleScriptProcessor,
    AutomatorProcessor,
    CropProcessor,
    ESRGANProcessor,
    ExpandProcessor,
    ModeProcessor,
    PngquantProcessor,
    ResizeProcessor,
    SideChannelProcessor,
    SolidColorProcessor,
    TexconvProcessor,
    WaifuExternalProcessor,
    WaifuProcessor,
    XbrzProcessor,
)

###################################### VARIABLES #######################################
infiles = {
    f[:-4].upper(): join(getcwd(), "data", "infiles", f)
    for f in ["l.png", "la.png", "rgb.png", "rgba.png"]
}
esrgan_models = {
    f[:-4]: join(getcwd(), "data", "models", f)
    for f in ["1x_BC1-smooth2.pth", "RRDB_ESRGAN_x4.pth", "RRDB_ESRGAN_x4_old_arch.pth"]
}


####################################### FIXTURES #######################################
@pytest.fixture(
    params=[
        AppleScriptProcessor,
        AutomatorProcessor,
        CropProcessor,
        ESRGANProcessor,
        ExpandProcessor,
        ModeProcessor,
        PngquantProcessor,
        # PotraceProcessor,
        ResizeProcessor,
        SideChannelProcessor,
        SolidColorProcessor,
        TexconvProcessor,
        # ThresholdProcessor,
        WaifuProcessor,
        WaifuExternalProcessor,
        XbrzProcessor,
    ]
)
def processor(request):
    return request.param


@pytest.fixture(params=infiles.keys())
def infile(request):
    return infiles[request.param]


######################################## TESTS #########################################
def test_help(processor: Processor) -> None:
    command = f"python {getfile(processor)} -h"
    child = Popen(command, shell=True)
    exitcode = child.wait()
    if exitcode != 0:
        raise ValueError()


def test_crop(infile: str) -> None:
    with temporary_filename(".png") as outfile:
        input_image = Image.open(infile)

        command = f"python {getfile(CropProcessor)} -vv "
        command += " --pixels 4 4 4 4"
        command += f" {infile} {outfile}"
        child = Popen(command, shell=True)
        exitcode = child.wait()
        assert exitcode == 0

        with Image.open(outfile) as output_image:
            assert input_image.mode == output_image.mode


@pytest.mark.parametrize(
    ("infile", "model_infile"),
    [
        (infiles["L"], esrgan_models["1x_BC1-smooth2"]),
        (infiles["L"], esrgan_models["RRDB_ESRGAN_x4"]),
        (infiles["L"], esrgan_models["RRDB_ESRGAN_x4_old_arch"]),
        pytest.param(
            infiles["LA"], esrgan_models["1x_BC1-smooth2"], marks=pytest.mark.xfail,
        ),
        (infiles["RGB"], esrgan_models["1x_BC1-smooth2"]),
        (infiles["RGB"], esrgan_models["RRDB_ESRGAN_x4"]),
        (infiles["RGB"], esrgan_models["RRDB_ESRGAN_x4_old_arch"]),
        pytest.param(
            infiles["RGBA"], esrgan_models["1x_BC1-smooth2"], marks=pytest.mark.xfail,
        ),
    ],
)
def test_esrgan(infile: str, model_infile: str) -> None:
    with temporary_filename(".png") as outfile:
        input_image = Image.open(infile)

        command = f"python {getfile(ESRGANProcessor)} -vv"
        command += f" --model {model_infile}"
        command += f" {infile} {outfile}"
        child = Popen(command, shell=True)
        exitcode = child.wait()
        assert exitcode == 0

        with Image.open(outfile) as output_image:
            assert input_image.mode == output_image.mode


def test_expand(infile: str) -> None:
    with temporary_filename(".png") as outfile:
        input_image = Image.open(infile)

        command = f"python {getfile(ExpandProcessor)} -vv"
        command += " --pixels 4 4 4 4"
        command += f" {infile} {outfile}"
        child = Popen(command, shell=True)
        exitcode = child.wait()
        assert exitcode == 0

        with Image.open(outfile) as output_image:
            assert input_image.mode == output_image.mode


def test_pngquant(infile: str) -> None:
    with temporary_filename(".png") as outfile:
        input_image = Image.open(infile)

        command = f"python {getfile(PngquantProcessor)} -vv"
        command += f" {infile} {outfile}"
        child = Popen(command, shell=True)
        exitcode = child.wait()
        assert exitcode == 0

        with Image.open(outfile) as output_image:
            assert output_image.size == input_image.size
            assert output_image.mode in (input_image.mode, "P")
            assert getsize(outfile) <= getsize(infile)


def test_resize(infile: str) -> None:
    with temporary_filename(".png") as outfile:
        input_image = Image.open(infile)

        command = f"python {getfile(ResizeProcessor)} -vv"
        command += " --scale 2"
        command += f" {infile} {outfile}"
        child = Popen(command, shell=True)
        exitcode = child.wait()
        assert exitcode == 0

        with Image.open(outfile) as output_image:
            assert input_image.mode == output_image.mode
            assert input_image.size[0] * 2 == output_image.size[0]
            assert input_image.size[1] * 2 == output_image.size[1]


def test_solid_color(infile: str) -> None:
    with temporary_filename(".png") as outfile:
        input_image = Image.open(infile)

        command = f"python {getfile(SolidColorProcessor)} -vv"
        command += f" {infile} {outfile}"
        child = Popen(command, shell=True)
        exitcode = child.wait()
        assert exitcode == 0

        with Image.open(outfile) as output_image:
            assert len(output_image.getcolors()) == 1
            assert input_image.mode == output_image.mode


@pytest.mark.skipif(not any(win32_ver()), reason="Processor only supported on Windows")
def test_texconv(infile: str) -> None:
    with temporary_filename(".png") as outfile:
        input_image = Image.open(infile)

        command = f"python {getfile(TexconvProcessor)} -vv"
        command += f" {infile} {outfile}"
        child = Popen(command, shell=True)
        exitcode = child.wait()
        assert exitcode == 0

        with Image.open(outfile) as output_image:
            assert output_image.mode == "RGBA"


@pytest.mark.parametrize(
    ("infile", "architecture", "denoise", "scale"),
    [
        (infiles["L"], "resnet10", 0, 2),
        (infiles["L"], "upconv7", 0, 2),
        (infiles["L"], "upresnet10", 0, 2),
        (infiles["L"], "vgg7", 0, 2),
        (infiles["L"], "resnet10", 0, 1),
        (infiles["L"], "upconv7", 1, 2),
        (infiles["L"], "upresnet10", 2, 2),
        (infiles["L"], "vgg7", 3, 2),
        pytest.param(infiles["LA"], "resnet10", 0, 2, marks=pytest.mark.xfail),
        (infiles["RGB"], "resnet10", 0, 2,),
        (infiles["RGB"], "upconv7", 0, 2,),
        (infiles["RGB"], "upresnet10", 0, 2,),
        (infiles["RGB"], "vgg7", 0, 2,),
        (infiles["RGB"], "resnet10", 0, 1,),
        (infiles["RGB"], "upconv7", 1, 2,),
        (infiles["RGB"], "upresnet10", 2, 2,),
        (infiles["RGB"], "vgg7", 3, 2,),
        pytest.param(infiles["RGBA"], "resnet10", 0, 2, marks=pytest.mark.xfail),
    ],
)
def test_waifu(infile: str, architecture: str, denoise: int, scale: int) -> None:
    with temporary_filename(".png") as outfile:
        input_image = Image.open(infile)

        command = f"python {getfile(WaifuProcessor)} -vv"
        command += f" --architecture {architecture}"
        command += f" --denoise {denoise}"
        command += f" --scale {scale}"
        command += f" {infile} {outfile}"
        child = Popen(command, shell=True)
        exitcode = child.wait()
        assert exitcode == 0

        with Image.open(outfile) as output_image:
            assert input_image.mode == output_image.mode


@pytest.mark.parametrize(
    ("infile", "imagetype", "denoise", "scale"),
    [
        (infiles["L"], "a", 0, 2),
        (infiles["L"], "a", 3, 2),
        pytest.param(infiles["LA"], "a", 0, 2, marks=pytest.mark.xfail),
        (infiles["RGB"], "a", 0, 2,),
        (infiles["RGB"], "a", 3, 2,),
        pytest.param(infiles["RGBA"], "a", 0, 2, marks=pytest.mark.xfail),
    ],
)
def test_waifu_external(infile: str, imagetype: str, denoise: int, scale: int) -> None:
    with temporary_filename(".png") as outfile:
        input_image = Image.open(infile)

        command = f"python {getfile(WaifuExternalProcessor)} -vv"
        command += f" --type {imagetype}"
        command += f" --denoise {denoise}"
        command += f" --scale {scale}"
        command += f" {infile} {outfile}"
        child = Popen(command, shell=True)
        exitcode = child.wait()
        assert exitcode == 0

        with Image.open(outfile) as output_image:
            assert input_image.mode == output_image.mode
            assert input_image.size[0] * scale == output_image.size[0]
            assert input_image.size[1] * scale == output_image.size[1]


def test_xbrz(infile: str) -> None:
    with temporary_filename(".png") as outfile:
        input_image = Image.open(infile)

        command = f"python {getfile(XbrzProcessor)} -vv"
        command += f" {infile} {outfile}"
        child = Popen(command, shell=True)
        exitcode = child.wait()
        assert exitcode == 0

        with Image.open(outfile) as output_image:
            assert input_image.mode == output_image.mode
