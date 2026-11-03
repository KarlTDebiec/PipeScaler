#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for image command-line interface."""

from __future__ import annotations

import pytest

from pipescaler.common.cli import CommandLineInterface
from pipescaler.image.cli import (
    ImageCli,
    ImageMergersCli,
    ImageProcessorsCli,
    ImageSplittersCli,
)
from test.helpers import assert_cli_help, assert_cli_usage


@pytest.mark.parametrize(
    "commands",
    [
        (ImageCli,),
        (ImageCli, ImageMergersCli),
        (ImageCli, ImageProcessorsCli),
        (ImageCli, ImageSplittersCli),
    ],
)
def test_help(commands: tuple[type[CommandLineInterface], ...]):
    """Test that help flag displays usage information and exits successfully.

    Arguments:
        commands: Tuple of command-line interface classes to test
    """
    assert_cli_help(commands)


@pytest.mark.parametrize(
    "commands",
    [
        (ImageCli,),
        (ImageCli, ImageMergersCli),
        (ImageCli, ImageProcessorsCli),
        (ImageCli, ImageSplittersCli),
    ],
)
def test_usage(commands: tuple[type[CommandLineInterface], ...]):
    """Test that running without arguments displays usage and exits with error.

    Arguments:
        commands: Tuple of command-line interface classes to test
    """
    assert_cli_usage(commands)


def test_rejects_unimplemented_utility_category(capsys: pytest.CaptureFixture[str]):
    """Reject the unimplemented image utility command.

    Arguments:
        capsys: captured command output
    """
    with pytest.raises(SystemExit) as exc:
        ImageCli.main(["utility"])

    assert exc.value.code == 2
    assert "invalid choice: 'utility'" in capsys.readouterr().err
