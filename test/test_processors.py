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
from os.path import getsize
from platform import win32_ver
from subprocess import PIPE, Popen

import numpy as np
import pytest
from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.core import (
    Processor,
    remove_palette_from_image,
)
from pipescaler.processors import (
    CropProcessor,
    ESRGANProcessor,
    ExpandProcessor,
    HeightToNormalProcessor,
    ModeProcessor,
    PngquantProcessor,
    ResizeProcessor,
    SolidColorProcessor,
    TexconvProcessor,
    WaifuExternalProcessor,
    WaifuProcessor,
    XbrzProcessor,
)

# noinspection PyUnresolvedReferences
from shared import (
    infiles,
    processor,
    infile,
    esrgan,
    xfail_assertion,
    xfail_unsupported_mode,
)


######################################## TESTS #########################################
def test_help(processor: Processor) -> None:
    command = f"coverage run {getfile(processor)} -h"
    child = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
    exitcode = child.wait()
    if exitcode != 0:
        raise ValueError()


def test_crop(infile: str) -> None:
    with temporary_filename(".png") as outfile:
        input_image = Image.open(infile)

        command = (
            f"coverage run {getfile(CropProcessor)} "
            " --pixels 4 4 4 4"
            f" {infile} {outfile}"
        )
        child = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        exitcode = child.wait()
        assert exitcode == 0

        with Image.open(outfile) as output_image:
            assert output_image.mode == input_image.mode
            assert output_image.size[0] == input_image.size[0] - 4 - 4
            assert output_image.size[1] == input_image.size[1] - 4 - 4


@pytest.mark.parametrize(
    ("infile", "model_infile", "scale"),
    [
        (infiles["L"], esrgan["1x_BC1-smooth2"], 1),
        (infiles["PL"], esrgan["1x_BC1-smooth2"], 1),
        (infiles["PRGB"], esrgan["1x_BC1-smooth2"], 1),
        (infiles["RGB"], esrgan["1x_BC1-smooth2"], 1),
        (infiles["RGB"], esrgan["RRDB_ESRGAN_x4"], 4),
        (infiles["RGB"], esrgan["RRDB_ESRGAN_x4_old_arch"], 4),
        xfail_assertion(infiles["LA"], esrgan["1x_BC1-smooth2"], 1),
        xfail_assertion(infiles["PLA"], esrgan["1x_BC1-smooth2"], 1),
        xfail_assertion(infiles["PRGBA"], esrgan["1x_BC1-smooth2"], 1),
        xfail_assertion(infiles["RGBA"], esrgan["1x_BC1-smooth2"], 1),
    ],
)
def test_esrgan(infile: str, model_infile: str, scale: int) -> None:
    with temporary_filename(".png") as outfile:
        input_image = Image.open(infile)
        if input_image.mode == "P":
            expected_output_mode = remove_palette_from_image(input_image).mode
        else:
            expected_output_mode = input_image.mode
        command = (
            f"coverage run {getfile(ESRGANProcessor)}"
            f" --model {model_infile}"
            f" {infile} {outfile}"
        )
        child = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        exitcode = child.wait()
        assert exitcode == 0

        with Image.open(outfile) as output_image:
            assert output_image.mode == expected_output_mode
            assert output_image.size[0] == input_image.size[0] * scale
            assert output_image.size[1] == input_image.size[1] * scale


def test_expand(infile: str) -> None:
    with temporary_filename(".png") as outfile:
        input_image = Image.open(infile)

        command = (
            f"coverage run {getfile(ExpandProcessor)}"
            " --pixels 4 4 4 4"
            f" {infile} {outfile}"
        )
        child = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        exitcode = child.wait()
        assert exitcode == 0

        with Image.open(outfile) as output_image:
            assert input_image.mode == output_image.mode
            assert output_image.size[0] == input_image.size[0] + 4 + 4
            assert output_image.size[1] == input_image.size[1] + 4 + 4


@pytest.mark.parametrize(
    ("infile", "sigma"),
    [
        (infiles["L"], 0.5),
        (infiles["L"], 1.0),
        xfail_assertion(infiles["LA"], 1.0),
        (infiles["PL"], 1.0),
        xfail_assertion(infiles["PLA"], 1.0),
        xfail_assertion(infiles["PRGB"], 1.0),
        xfail_assertion(infiles["PRGBA"], 1.0),
        xfail_assertion(infiles["RGB"], 1.0),
        xfail_assertion(infiles["RGBA"], 1.0),
    ],
)
def test_height_to_normal(infile: str, sigma: float) -> None:
    with temporary_filename(".png") as outfile:
        input_image = Image.open(infile)

        command = (
            f"coverage run {getfile(HeightToNormalProcessor)}"
            f" --sigma {sigma}"
            f" {infile} {outfile}"
        )
        child = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        exitcode = child.wait()
        assert exitcode == 0

        with Image.open(outfile) as output_image:
            output_datum = np.array(output_image)
            assert output_image.mode == "RGB"
            assert output_image.size == input_image.size
            assert np.min(output_datum[:, :, 2] >= 128)


@pytest.mark.parametrize(
    ("infile", "mode"),
    [
        (infiles["L"], "L"),
        (infiles["L"], "LA"),
        (infiles["L"], "RGB"),
        (infiles["L"], "RGBA"),
        (infiles["LA"], "L"),
        (infiles["LA"], "LA"),
        (infiles["LA"], "RGB"),
        (infiles["LA"], "RGBA"),
        (infiles["PL"], "RGBA"),
        (infiles["PLA"], "RGBA"),
        (infiles["PRGB"], "RGBA"),
        (infiles["PRGBA"], "RGBA"),
        (infiles["RGB"], "L"),
        (infiles["RGB"], "LA"),
        (infiles["RGB"], "RGB"),
        (infiles["RGB"], "RGBA"),
        (infiles["RGBA"], "L"),
        (infiles["RGBA"], "LA"),
        (infiles["RGBA"], "RGB"),
        (infiles["RGBA"], "RGBA"),
    ],
)
def test_mode(infile: str, mode: str) -> None:
    with temporary_filename(".png") as outfile:
        input_image = Image.open(infile)

        command = (
            f"coverage run {getfile(ModeProcessor)}"
            f" --mode {mode}"
            f" {infile} {outfile}"
        )
        child = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        exitcode = child.wait()
        assert exitcode == 0

        with Image.open(outfile) as output_image:
            assert output_image.size == input_image.size
            assert output_image.mode == mode


def test_pngquant(infile: str) -> None:
    with temporary_filename(".png") as outfile:
        input_image = Image.open(infile)

        command = f"coverage run {getfile(PngquantProcessor)} {infile} {outfile}"
        child = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        exitcode = child.wait()
        assert exitcode == 0

        with Image.open(outfile) as output_image:
            assert output_image.mode in (input_image.mode, "P")
            assert output_image.size == input_image.size
            assert getsize(outfile) <= getsize(infile)


def test_resize(infile: str) -> None:
    with temporary_filename(".png") as outfile:
        input_image = Image.open(infile)
        if input_image.mode == "P":
            expected_output_mode = remove_palette_from_image(input_image).mode
        else:
            expected_output_mode = input_image.mode
        command = (
            f"coverage run {getfile(ResizeProcessor)}"
            " --scale 2"
            f" {infile} {outfile}"
        )
        child = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        exitcode = child.wait()
        assert exitcode == 0

        with Image.open(outfile) as output_image:
            assert output_image.mode == expected_output_mode
            assert output_image.size[0] == input_image.size[0] * 2
            assert output_image.size[1] == input_image.size[1] * 2


def test_solid_color(infile: str) -> None:
    with temporary_filename(".png") as outfile:
        input_image = Image.open(infile)
        if input_image.mode == "P":
            expected_output_mode = remove_palette_from_image(input_image).mode
        else:
            expected_output_mode = input_image.mode

        command = f"coverage run {getfile(SolidColorProcessor)} {infile} {outfile}"
        child = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        exitcode = child.wait()
        assert exitcode == 0

        with Image.open(outfile) as output_image:
            assert output_image.mode == expected_output_mode
            assert output_image.size[0] == input_image.size[0]
            assert output_image.size[1] == input_image.size[1]
            assert len(output_image.getcolors()) == 1


@pytest.mark.skipif(not any(win32_ver()), reason="Processor only supported on Windows")
def test_texconv(infile: str) -> None:
    with temporary_filename(".png") as outfile:
        input_image = Image.open(infile)

        command = f"coverage run {getfile(TexconvProcessor)} {infile} {outfile}"
        child = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        exitcode = child.wait()
        assert exitcode == 0

        with Image.open(outfile) as output_image:
            assert output_image.mode == "RGBA"
            assert output_image.size[0] == input_image.size[0]
            assert output_image.size[1] == input_image.size[1]


@pytest.mark.parametrize(
    ("infile", "architecture", "denoise", "scale"),
    [
        (infiles["L"], "resnet10", 0, 2),
        (infiles["PL"], "resnet10", 0, 2),
        (infiles["PRGB"], "resnet10", 0, 2),
        (infiles["RGB"], "resnet10", 0, 2,),
        (infiles["RGB"], "upconv7", 0, 2,),
        (infiles["RGB"], "upresnet10", 0, 2,),
        (infiles["RGB"], "vgg7", 0, 2,),
        (infiles["RGB"], "resnet10", 0, 1,),
        (infiles["RGB"], "upconv7", 1, 2,),
        (infiles["RGB"], "upresnet10", 2, 2,),
        (infiles["RGB"], "vgg7", 3, 2,),
        xfail_assertion(infiles["LA"], "resnet10", 0, 2),
        xfail_assertion(infiles["PLA"], "resnet10", 0, 2),
        xfail_assertion(infiles["PRGBA"], "resnet10", 0, 2),
        xfail_assertion(infiles["RGBA"], "resnet10", 0, 2),
    ],
)
def test_waifu(infile: str, architecture: str, denoise: int, scale: int) -> None:
    with temporary_filename(".png") as outfile:
        input_image = Image.open(infile)
        if input_image.mode == "P":
            expected_output_mode = remove_palette_from_image(input_image).mode
        else:
            expected_output_mode = input_image.mode

        command = (
            f"coverage run {getfile(WaifuProcessor)}"
            f" --architecture {architecture}"
            f" --denoise {denoise}"
            f" --scale {scale}"
            f" {infile} {outfile}"
        )
        child = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        exitcode = child.wait()
        assert exitcode == 0

        with Image.open(outfile) as output_image:
            assert output_image.mode == expected_output_mode
            assert output_image.size[0] == input_image.size[0] * scale
            assert output_image.size[1] == input_image.size[1] * scale


@pytest.mark.parametrize(
    ("infile", "imagetype", "denoise", "scale"),
    [
        (infiles["L"], "a", 0, 2),
        (infiles["PL"], "a", 0, 2),
        (infiles["PRGB"], "a", 0, 2),
        (infiles["RGB"], "a", 0, 2,),
        (infiles["RGB"], "a", 3, 2,),
        xfail_assertion(infiles["LA"], "a", 0, 2),
        xfail_assertion(infiles["PLA"], "a", 0, 2),
        xfail_assertion(infiles["PRGBA"], "a", 0, 2),
        xfail_assertion(infiles["RGBA"], "a", 0, 2),
    ],
)
def test_waifu_external(infile: str, imagetype: str, denoise: int, scale: int) -> None:
    with temporary_filename(".png") as outfile:
        input_image = Image.open(infile)
        if input_image.mode == "P":
            expected_output_mode = remove_palette_from_image(input_image).mode
        else:
            expected_output_mode = input_image.mode

        command = (
            f"coverage run {getfile(WaifuExternalProcessor)}"
            f" --type {imagetype}"
            f" --denoise {denoise}"
            f" --scale {scale}"
            f" {infile} {outfile}"
        )
        child = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        exitcode = child.wait()
        assert exitcode == 0

        with Image.open(outfile) as output_image:
            assert output_image.mode == expected_output_mode
            assert output_image.size[0] == input_image.size[0] * scale
            assert output_image.size[1] == input_image.size[1] * scale


def test_xbrz(infile: str) -> None:
    with temporary_filename(".png") as outfile:
        input_image = Image.open(infile)
        if input_image.mode == "P":
            expected_output_mode = remove_palette_from_image(input_image).mode
        else:
            expected_output_mode = input_image.mode

        command = (
            f"coverage run {getfile(XbrzProcessor)}"
            f" --scale 2"
            f" {infile} {outfile}"
        )

        child = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        exitcode = child.wait()
        assert exitcode == 0

        with Image.open(outfile) as output_image:
            assert output_image.mode == expected_output_mode
            assert output_image.size[0] == input_image.size[0] * 2
            assert output_image.size[1] == input_image.size[1] * 2
