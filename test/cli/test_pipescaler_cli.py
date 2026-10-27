#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for PipeScaler command-line interface."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from inspect import getfile
from io import StringIO
from pathlib import Path

import pytest
from PIL import Image

from pipescaler.cli import PipeScalerCli
from pipescaler.common import CommandLineInterface
from pipescaler.common.testing import run_cli_with_args
from pipescaler.image.cli import ImageCli
from pipescaler.testing.mark import parametrize_with_readable_ids


def test_image_processing_split_and_merge(tmp_path: Path):
    """Dispatch image operations through the root command and preserve pixels.

    Arguments:
        tmp_path: temporary test directory
    """
    input_path = tmp_path / "input.png"
    resized_path = tmp_path / "resized.png"
    color_path = tmp_path / "color.png"
    alpha_path = tmp_path / "alpha.png"
    merged_path = tmp_path / "merged.png"
    image = Image.new("RGBA", (2, 3), (20, 40, 60, 128))
    image.save(input_path)

    PipeScalerCli.main(
        [
            "image",
            "process",
            "resize",
            str(input_path),
            str(resized_path),
            "--scale",
            "2",
            "--resample",
            "nearest",
        ]
    )
    PipeScalerCli.main(
        [
            "image",
            "split",
            "alphasplitter",
            str(resized_path),
            str(color_path),
            str(alpha_path),
        ]
    )
    PipeScalerCli.main(
        [
            "image",
            "merge",
            "alphamerger",
            str(color_path),
            str(alpha_path),
            str(merged_path),
        ]
    )

    with Image.open(merged_path) as merged_image:
        assert merged_image.mode == "RGBA"
        assert merged_image.size == (4, 6)
        assert (
            merged_image.tobytes()
            == Image.new("RGBA", (4, 6), (20, 40, 60, 128)).tobytes()
        )


@parametrize_with_readable_ids(
    "commands",
    [
        (PipeScalerCli,),
        (PipeScalerCli, ImageCli),
    ],
)
def test_help(commands: tuple[type[CommandLineInterface], ...]):
    """Test that help flag displays usage information and exits successfully.

    Arguments:
        commands: Tuple of command-line interface classes to test
    """
    subcommands = " ".join(f"{command.name()}" for command in commands[1:])

    stdout = StringIO()
    stderr = StringIO()
    try:
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                run_cli_with_args(commands[0], f"{subcommands} -h")
    except SystemExit as exc:
        assert exc.code == 0
        assert stdout.getvalue().startswith(
            f"usage: {Path(getfile(commands[0])).name} {subcommands}"
        )
        assert stderr.getvalue() == ""


@pytest.mark.parametrize(
    "commands",
    [
        (PipeScalerCli,),
        (PipeScalerCli, ImageCli),
    ],
)
def test_usage(commands: tuple[type[CommandLineInterface], ...]):
    """Test that running without arguments displays usage and exits with error.

    Arguments:
        commands: Tuple of command-line interface classes to test
    """
    subcommands = " ".join(f"{command.name()}" for command in commands[1:])

    stdout = StringIO()
    stderr = StringIO()
    try:
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                run_cli_with_args(commands[0], subcommands)
    except SystemExit as exc:
        assert exc.code == 2
        assert stdout.getvalue() == ""
        assert stderr.getvalue().startswith(
            f"usage: {Path(getfile(commands[0])).name} {subcommands}"
        )
