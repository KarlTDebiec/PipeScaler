#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared help and missing-argument checks for image command adapters."""

from __future__ import annotations

from collections.abc import Callable

import pytest

from pipescaler.common.cli import CommandLineInterface
from pipescaler.image.cli import ImageMergersCli, ImageProcessorsCli, ImageSplittersCli
from pipescaler.image.cli.mergers import (
    AlphaMergerCli,
    DiffMergerCli,
    PaletteMatchMergerCli,
)
from pipescaler.image.cli.processors import (
    CropCli,
    ExpandCli,
    HeightToNormalCli,
    ImagequantCli,
    ModeCli,
    ResizeCli,
    SharpenCli,
    SolidColorCli,
    SpandrelCli,
    ThresholdCli,
    XbrzCli,
)
from pipescaler.image.cli.splitters import AlphaSplitterCli
from test.helpers import assert_cli_help, assert_cli_usage


@pytest.mark.parametrize(
    "check", [assert_cli_help, assert_cli_usage], ids=["help", "usage"]
)
@pytest.mark.parametrize(
    "commands",
    [
        commands
        for parent, children in [
            (
                ImageProcessorsCli,
                (
                    CropCli,
                    ExpandCli,
                    HeightToNormalCli,
                    ImagequantCli,
                    ModeCli,
                    ResizeCli,
                    SharpenCli,
                    SolidColorCli,
                    SpandrelCli,
                    ThresholdCli,
                    XbrzCli,
                ),
            ),
            (ImageMergersCli, (AlphaMergerCli, DiffMergerCli, PaletteMatchMergerCli)),
            (ImageSplittersCli, (AlphaSplitterCli,)),
        ]
        for commands in [
            (parent,),
            *((child,) for child in children),
            *((parent, child) for child in children),
        ]
    ],
    ids=lambda commands: "-".join(command.__name__ for command in commands),
)
def test_help_and_usage(
    commands: tuple[type[CommandLineInterface], ...],
    check: Callable[[tuple[type[CommandLineInterface], ...]], None],
):
    """Verify each built-in command directly and through its parent dispatcher.

    Arguments:
        commands: explicitly expected built-in command hierarchy
        check: help or missing-argument assertion
    """
    check(commands)
