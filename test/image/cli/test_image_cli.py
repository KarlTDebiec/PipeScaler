#  Copyright 2020-2023 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Tests for image command-line interfaces."""
from typing import Type

import pytest

from pipescaler.common import CommandLineInterface
from pipescaler.image.cli import ImageCli
from pipescaler.testing import run_cli_with_args, xfail_system_exit


@pytest.mark.parametrize(
    ("cli", "args"),
    [
        xfail_system_exit()(ImageCli, ""),
        xfail_system_exit()(ImageCli, "-h"),
        xfail_system_exit()(ImageCli, "process"),
        xfail_system_exit()(ImageCli, "process -h"),
        xfail_system_exit()(ImageCli, "utility"),
        xfail_system_exit()(ImageCli, "utility -h"),
    ],
)
def test_help(cli: Type[CommandLineInterface], args: str):
    run_cli_with_args(cli, f"{args}")
