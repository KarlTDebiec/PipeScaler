#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Tests for usage text of command line interfaces."""
from contextlib import redirect_stderr, redirect_stdout
from inspect import getfile
from io import StringIO
from pathlib import Path
from typing import Type

from pipescaler.cli import PipeScalerCli, ProcessorsCli, UtilitiesCli
from pipescaler.cli.processors import (
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
    WebCli,
    XbrzCli,
)
from pipescaler.cli.utilities import (
    ApngCreatorCli,
    EsrganSerializerCli,
    HostCli,
    WaifuSerializerCli,
)
from pipescaler.common import CommandLineInterface
from pipescaler.testing import parametrize_with_readable_ids, run_cli_with_args


@parametrize_with_readable_ids(
    ("commands"),
    [
        ((ApngCreatorCli,)),
        ((CropCli,)),
        ((EsrganCli,)),
        ((EsrganSerializerCli,)),
        ((ExpandCli,)),
        ((HeightToNormalCli,)),
        ((HostCli,)),
        ((ModeCli,)),
        ((PipeScalerCli,)),
        ((ProcessorsCli,)),
        ((ResizeCli,)),
        ((SharpenCli,)),
        ((SolidColorCli,)),
        ((ThresholdCli,)),
        ((UtilitiesCli,)),
        ((WaifuCli,)),
        ((WaifuSerializerCli,)),
        ((WebCli,)),
        ((XbrzCli,)),
        ((ProcessorsCli, CropCli)),
        ((ProcessorsCli, EsrganCli)),
        ((ProcessorsCli, ExpandCli)),
        ((ProcessorsCli, HeightToNormalCli)),
        ((ProcessorsCli, ModeCli)),
        ((ProcessorsCli, ResizeCli)),
        ((ProcessorsCli, SharpenCli)),
        ((ProcessorsCli, SolidColorCli)),
        ((ProcessorsCli, ThresholdCli)),
        ((ProcessorsCli, WaifuCli)),
        ((ProcessorsCli, WebCli)),
        ((ProcessorsCli, XbrzCli)),
        ((UtilitiesCli, ApngCreatorCli)),
        ((UtilitiesCli, EsrganSerializerCli)),
        ((UtilitiesCli, HostCli)),
        ((UtilitiesCli, WaifuSerializerCli)),
        ((PipeScalerCli, ProcessorsCli)),
        ((PipeScalerCli, ProcessorsCli, CropCli)),
        ((PipeScalerCli, ProcessorsCli, EsrganCli)),
        ((PipeScalerCli, ProcessorsCli, ExpandCli)),
        ((PipeScalerCli, ProcessorsCli, HeightToNormalCli)),
        ((PipeScalerCli, ProcessorsCli, ModeCli)),
        ((PipeScalerCli, ProcessorsCli, ResizeCli)),
        ((PipeScalerCli, ProcessorsCli, SharpenCli)),
        ((PipeScalerCli, ProcessorsCli, SolidColorCli)),
        ((PipeScalerCli, ProcessorsCli, ThresholdCli)),
        ((PipeScalerCli, ProcessorsCli, WaifuCli)),
        ((PipeScalerCli, ProcessorsCli, WebCli)),
        ((PipeScalerCli, ProcessorsCli, XbrzCli)),
        ((PipeScalerCli, UtilitiesCli)),
        ((PipeScalerCli, UtilitiesCli, ApngCreatorCli)),
        ((PipeScalerCli, UtilitiesCli, EsrganSerializerCli)),
        ((PipeScalerCli, UtilitiesCli, HostCli)),
        ((PipeScalerCli, UtilitiesCli, WaifuSerializerCli)),
    ],
)
def test(commands: tuple[Type[CommandLineInterface], ...]) -> None:
    subcommands = " ".join(f"{command.name()}" for command in commands[1:])

    stdout = StringIO()
    stderr = StringIO()
    try:
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                run_cli_with_args(commands[0], subcommands)
    except SystemExit as error:
        assert error.code == 2
        assert stdout.getvalue() == ""
        assert stderr.getvalue().startswith(
            f"usage: {Path(getfile(commands[0])).name} {subcommands}"
        )
