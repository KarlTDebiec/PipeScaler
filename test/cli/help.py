#  Copyright 2020-2023 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Tests for help text of command-line interfaces."""
from contextlib import redirect_stderr, redirect_stdout
from inspect import getfile
from io import StringIO
from pathlib import Path
from typing import Type

from pipescaler.cli import PipeScalerCli
from pipescaler.common import CommandLineInterface
from pipescaler.image.cli.image_processors_cli import ImageProcessorsCli
from pipescaler.image.cli.image_utilities_cli import ImageUtilitiesCli
from pipescaler.image.cli.processors import (
    CropCli,
    EsrganCli,
    ExpandCli,
    HeightToNormalCli,
    ModeCli,
    ResizeCli,
    SharpenCli,
    SolidColorCli,
    ThresholdCli,
    WaifuCli,
    XbrzCli,
)
from pipescaler.image.cli.utilities import EsrganSerializerCli, WaifuSerializerCli
from pipescaler.testing import parametrize_with_readable_ids, run_cli_with_args
from pipescaler.video.cli.utilities import ApngCreatorCli


@parametrize_with_readable_ids(
    ("commands"),
    [
        ((ApngCreatorCli,)),
        ((CropCli,)),
        ((EsrganCli,)),
        ((EsrganSerializerCli,)),
        ((ExpandCli,)),
        ((HeightToNormalCli,)),
        ((ModeCli,)),
        ((PipeScalerCli,)),
        ((ImageProcessorsCli,)),
        ((ResizeCli,)),
        ((SharpenCli,)),
        ((SolidColorCli,)),
        ((ThresholdCli,)),
        ((ImageUtilitiesCli,)),
        ((WaifuCli,)),
        ((WaifuSerializerCli,)),
        ((XbrzCli,)),
        ((ImageProcessorsCli, CropCli)),
        ((ImageProcessorsCli, EsrganCli)),
        ((ImageProcessorsCli, ExpandCli)),
        ((ImageProcessorsCli, HeightToNormalCli)),
        ((ImageProcessorsCli, ModeCli)),
        ((ImageProcessorsCli, ResizeCli)),
        ((ImageProcessorsCli, SharpenCli)),
        ((ImageProcessorsCli, SolidColorCli)),
        ((ImageProcessorsCli, ThresholdCli)),
        ((ImageProcessorsCli, WaifuCli)),
        ((ImageProcessorsCli, XbrzCli)),
        ((ImageUtilitiesCli, ApngCreatorCli)),
        ((ImageUtilitiesCli, EsrganSerializerCli)),
        ((ImageUtilitiesCli, WaifuSerializerCli)),
        ((PipeScalerCli, ImageProcessorsCli)),
        ((PipeScalerCli, ImageProcessorsCli, CropCli)),
        ((PipeScalerCli, ImageProcessorsCli, EsrganCli)),
        ((PipeScalerCli, ImageProcessorsCli, ExpandCli)),
        ((PipeScalerCli, ImageProcessorsCli, HeightToNormalCli)),
        ((PipeScalerCli, ImageProcessorsCli, ModeCli)),
        ((PipeScalerCli, ImageProcessorsCli, ResizeCli)),
        ((PipeScalerCli, ImageProcessorsCli, SharpenCli)),
        ((PipeScalerCli, ImageProcessorsCli, SolidColorCli)),
        ((PipeScalerCli, ImageProcessorsCli, ThresholdCli)),
        ((PipeScalerCli, ImageProcessorsCli, WaifuCli)),
        ((PipeScalerCli, ImageProcessorsCli, XbrzCli)),
        ((PipeScalerCli, ImageUtilitiesCli)),
        ((PipeScalerCli, ImageUtilitiesCli, ApngCreatorCli)),
        ((PipeScalerCli, ImageUtilitiesCli, EsrganSerializerCli)),
        ((PipeScalerCli, ImageUtilitiesCli, WaifuSerializerCli)),
    ],
)
def test(commands: tuple[Type[CommandLineInterface], ...]) -> None:
    subcommands = " ".join(f"{command.name()}" for command in commands[1:])

    stdout = StringIO()
    stderr = StringIO()
    try:
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                run_cli_with_args(commands[0], f"{subcommands} -h")
    except SystemExit as error:
        assert error.code == 0
        assert stdout.getvalue().startswith(
            f"usage: {Path(getfile(commands[0])).name} {subcommands}"
        )
        assert stderr.getvalue() == ""
