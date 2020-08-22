#!/usr/bin/env python
#   test.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from inspect import getfile
from os import getcwd
from os.path import join
from subprocess import Popen
from sys import platform

import pytest
from PIL import Image

from pipescaler.common.general import temporary_filename
from pipescaler.processors import (
    ESRGANProcessor, Pixelmator2xProcessor, PngquantProcessor,
    PotraceProcessor, ThresholdProcessor,
    WaifuPixelmator2xTransparentProcessor, WaifuProcessor, XbrzProcessor)


################################## FIXTURES ###################################
@pytest.fixture(params=[
    ESRGANProcessor, Pixelmator2xProcessor, PngquantProcessor,
    PotraceProcessor, ThresholdProcessor,
    WaifuPixelmator2xTransparentProcessor, WaifuProcessor, XbrzProcessor])
def processor(request):
    return request.param


@pytest.fixture(params=["1x_BC1-smooth2.pth", "RRDB_ESRGAN_x4.pth",
                        "RRDB_ESRGAN_x4_old_arch.pth"])
def esrgan_model(request):
    return join(getcwd(), "models", request.param)


@pytest.fixture(params=["l.png", "rgb.png", "rgba.png"])
def infile(request):
    return join(getcwd(), "data", "infiles", request.param)


#################################### TESTS ####################################
def test_help(processor):
    command = f"python {getfile(processor)} -h"
    Popen(command, shell=True).wait()


def test_esrgan(infile, esrgan_model):
    with temporary_filename(".png") as outfile:
        command = f"python {getfile(ESRGANProcessor)} -vv " \
                  f"--model {esrgan_model} " \
                  f"{infile} {outfile}"
        Popen(command, shell=True).wait()
        Image.open(outfile)


def test_pngquant(infile):
    with temporary_filename(".png") as outfile:
        command = f"python {getfile(PngquantProcessor)} -vv " \
                  f"{infile} {outfile}"
        Popen(command, shell=True).wait()
        Image.open(outfile)


def test_potrace(infile):
    with temporary_filename(".png") as outfile:
        command = f"python {getfile(PotraceProcessor)} -vv " \
                  f"{infile} {outfile}"
        Popen(command, shell=True).wait()
        Image.open(outfile)


def test_threshold(infile):
    with temporary_filename(".png") as outfile:
        command = f"python {getfile(ThresholdProcessor)} -vv " \
                  f"{infile} {outfile}"
        Popen(command, shell=True).wait()
        Image.open(outfile)


@pytest.mark.skipif(platform != "darwin",
                    reason="Application only available on macOS")
def test_pixelmator(infile):
    with temporary_filename(".png") as outfile:
        command = f"python {getfile(Pixelmator2xProcessor)} -vv " \
                  f"{infile} {outfile}"
        Popen(command, shell=True).wait()
        Image.open(outfile)


@pytest.mark.skipif(platform != "darwin",
                    reason="Processor on implemented on macOS")
def test_waifu(infile):
    with temporary_filename(".png") as outfile:
        command = f"python {getfile(WaifuProcessor)} -vv " \
                  f"{infile} {outfile}"
        Popen(command, shell=True).wait()
        Image.open(outfile)


def test_xbrz(infile):
    with temporary_filename(".png") as outfile:
        command = f"python {getfile(XbrzProcessor)} -vv " \
                  f"{infile} {outfile}"
        Popen(command, shell=True).wait()
        Image.open(outfile)
