#!/usr/bin/env python
#   test_processors_cl.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
from inspect import getfile
from typing import Any

import pytest
from shared import esrgan_models, infiles, skip_if_ci, xfail_if_platform

from pipescaler.common import run_command, temporary_filename
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
    XbrzProcessor,
)


def run_processor_on_command_line(processor: Any, args: str, infile: str):
    with temporary_filename(".png") as outfile:
        command = f"coverage run {getfile(processor)} {args} {infile} {outfile}"
        run_command(command)


@pytest.mark.parametrize(
    ("infile", "args"),
    [
        (infiles["RGB"], "-h"),
        xfail_if_platform({"Linux", "Windows"}, raises=ValueError)(
            infiles["RGB"], "--script pixelmator/ml_super_resolution.scpt --args 2"
        ),
    ],
)
def test_apple_script_external(infile: str, args: str) -> None:
    run_processor_on_command_line(AppleScriptExternalProcessor, args, infile)


@pytest.mark.parametrize(
    ("infile", "args"),
    [
        (infiles["RGB"], "-h"),
        xfail_if_platform({"Linux", "Windows"}, raises=ValueError)(
            infiles["RGB"], "--workflow pixelmator/denoise.workflow"
        ),
    ],
)
def test_automator_external(infile: str, args: str) -> None:
    run_processor_on_command_line(AutomatorExternalProcessor, args, infile)


@pytest.mark.parametrize(
    ("infile", "args"),
    [(infiles["RGB"], "-h"), (infiles["RGB"], "--pixels 4 4 4 4")],
)
def test_crop(infile: str, args: str) -> None:
    run_processor_on_command_line(CropProcessor, args, infile)


@pytest.mark.serial
@pytest.mark.parametrize(
    ("infile", "args"),
    [
        (infiles["RGB"], "-h"),
        skip_if_ci()(infiles["RGB"], f"--model {esrgan_models['1x_BC1-smooth2']}"),
    ],
)
def test_esrgan(infile: str, args: str) -> None:
    run_processor_on_command_line(ESRGANProcessor, args, infile)


@pytest.mark.parametrize(
    ("infile", "args"),
    [(infiles["RGB"], "-h"), (infiles["RGB"], "--pixels 4 4 4 4")],
)
def test_expand(infile: str, args: str) -> None:
    run_processor_on_command_line(ExpandProcessor, args, infile)


@pytest.mark.parametrize(
    ("infile", "args"),
    [(infiles["L"], "-h"), (infiles["L"], "--sigma 1.0")],
)
def test_height_to_normal(infile: str, args: str) -> None:
    run_processor_on_command_line(HeightToNormalProcessor, args, infile)


@pytest.mark.parametrize(
    ("infile", "args"), [(infiles["RGB"], "-h"), (infiles["RGB"], "--mode L")]
)
def test_mode(infile: str, args: str) -> None:
    run_processor_on_command_line(ModeProcessor, args, infile)


@pytest.mark.parametrize(
    ("infile", "args"),
    [(infiles["RGB"], "-h"), skip_if_ci()(infiles["L"], "")],
)
def test_potrace_external(infile: str, args: str) -> None:
    run_processor_on_command_line(PotraceExternalProcessor, args, infile)


@pytest.mark.parametrize(
    ("infile", "args"),
    [
        (infiles["RGB"], "-h"),
        skip_if_ci()(infiles["RGB"], ""),
    ],
)
def test_pngquant_external(infile: str, args: str) -> None:
    run_processor_on_command_line(PngquantExternalProcessor, args, infile)


@pytest.mark.parametrize(
    ("infile", "args"),
    [
        (infiles["RGB"], "-h"),
        (infiles["RGB"], "--scale 2"),
    ],
)
def test_resize(infile: str, args: str) -> None:
    run_processor_on_command_line(ResizeProcessor, args, infile)


@pytest.mark.parametrize(
    ("infile", "args"),
    [(infiles["RGB"], "-h"), (infiles["RGB"], "")],
)
def test_solid_color(infile: str, args: str) -> None:
    run_processor_on_command_line(SolidColorProcessor, args, infile)


@pytest.mark.parametrize(
    ("infile", "args"),
    [
        (infiles["RGB"], "-h"),
        xfail_if_platform({"Darwin", "Linux"}, raises=ValueError)(infiles["RGB"], ""),
    ],
)
def test_texconv_external(infile: str, args: str) -> None:
    run_processor_on_command_line(TexconvExternalProcessor, args, infile)


@pytest.mark.parametrize(
    ("infile", "args"),
    [(infiles["RGB"], "-h"), (infiles["L"], "")],
)
def test_threshold(infile: str, args: str) -> None:
    run_processor_on_command_line(ThresholdProcessor, args, infile)


@pytest.mark.serial
@pytest.mark.parametrize(
    ("infile", "args"),
    [
        (infiles["RGB"], "-h"),
        skip_if_ci()(infiles["RGB"], f" --type a --denoise 0 --scale 2"),
    ],
)
def test_waifu_external(infile: str, args: str) -> None:
    run_processor_on_command_line(WaifuExternalProcessor, args, infile)


@pytest.mark.parametrize(
    ("infile", "args"),
    [(infiles["RGB"], "-h"), (infiles["RGB"], "--scale 2")],
)
def test_xbrz(infile: str, args: str) -> None:
    run_processor_on_command_line(XbrzProcessor, args, infile)
