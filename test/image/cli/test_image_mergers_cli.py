#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for merger command-line interfaces."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from inspect import getfile
from io import StringIO
from pathlib import Path

import pytest
from PIL import Image

from pipescaler.cli import PipeScalerCli
from pipescaler.common import CommandLineInterface
from pipescaler.common.file import get_temp_file_path
from pipescaler.common.testing import run_cli_with_args
from pipescaler.image.cli import ImageMergersCli
from pipescaler.image.cli.mergers import (
    AlphaMergerCli,
    DiffMergerCli,
    LocalPaletteMatchMergerCli,
    PaletteMatchMergerCli,
)
from pipescaler.testing.file import get_test_input_path


@pytest.mark.parametrize(
    ("cli", "args", "input_filenames"),
    [
        (AlphaMergerCli, "", ("RGB", "L")),
        (DiffMergerCli, "", ("RGB", "alt/RGB")),
        (PaletteMatchMergerCli, "", ("RGB", "alt/RGB")),
        (LocalPaletteMatchMergerCli, "", ("RGB", "alt/RGB")),
        (LocalPaletteMatchMergerCli, "--local-range 2", ("RGB", "alt/RGB")),
    ],
)
def test(cli: type[CommandLineInterface], args: str, input_filenames: tuple[str]):
    """Test merger CLI with various input files and arguments.

    Arguments:
        cli: The command-line interface class to test
        args: Command-line arguments string
        input_filenames: Tuple of input image filenames
    """
    input_paths = [
        str(get_test_input_path(input_filename)) for input_filename in input_filenames
    ]

    with (
        get_temp_file_path(".png") as output_path,
        get_temp_file_path(".png") as fit_path,
    ):
        if cli is LocalPaletteMatchMergerCli:
            with Image.open(input_paths[1]) as fit_img:
                fit_img.resize((fit_img.width * 2, fit_img.height * 2)).save(fit_path)
            input_paths[1] = str(fit_path)
        run_cli_with_args(cli, f"{args} {' '.join(input_paths)} {output_path}")


@pytest.mark.parametrize(
    "commands",
    [
        (AlphaMergerCli,),
        (DiffMergerCli,),
        (LocalPaletteMatchMergerCli,),
        (PaletteMatchMergerCli,),
        (ImageMergersCli,),
        (ImageMergersCli, AlphaMergerCli),
        (ImageMergersCli, DiffMergerCli),
        (ImageMergersCli, LocalPaletteMatchMergerCli),
        (ImageMergersCli, PaletteMatchMergerCli),
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
        (AlphaMergerCli,),
        (DiffMergerCli,),
        (LocalPaletteMatchMergerCli,),
        (PaletteMatchMergerCli,),
        (ImageMergersCli,),
        (ImageMergersCli, AlphaMergerCli),
        (ImageMergersCli, DiffMergerCli),
        (ImageMergersCli, LocalPaletteMatchMergerCli),
        (ImageMergersCli, PaletteMatchMergerCli),
    ],
)
def test_usage(commands: tuple[type[CommandLineInterface], ...]):
    """Test that missing arguments displays usage information and exits with error.

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


def test_diff_through_root_cli(tmp_path: Path):
    """Preserve signed pixels through root dispatch and saved RGB output.

    Arguments:
        tmp_path: temporary directory for input and output images
    """
    first_path = tmp_path / "first.png"
    second_path = tmp_path / "second.png"
    output_path = tmp_path / "diff.png"
    Image.new("L", (3, 1), 128).save(first_path)
    second = Image.new("L", (3, 1))
    second.putdata([0, 128, 255])
    second.save(second_path)
    PipeScalerCli.main(
        [
            "image",
            "merge",
            "diffmerger",
            str(first_path),
            str(second_path),
            str(output_path),
        ]
    )
    with Image.open(output_path) as output:
        assert output.mode == "RGB"
        red, same, blue = (output.getpixel((x, 0)) for x in (2, 1, 0))
        assert red[0] > 0 and red[2] == 0
        assert same == (0, 0, 0)
        assert blue[0] == 0 and blue[2] > 0


@pytest.mark.parametrize("local_range", ["0", "-1"])
def test_local_palette_range_rejected_during_parsing(local_range: str, tmp_path: Path):
    """Reject unsupported local ranges before attempting to run either backend.

    Arguments:
        local_range: invalid neighborhood radius
        tmp_path: temporary directory for input and output paths
    """
    input_path = get_test_input_path("L")
    with pytest.raises(SystemExit) as exc:
        LocalPaletteMatchMergerCli.argparser().parse_args(
            [
                "--local-range",
                local_range,
                str(input_path),
                str(input_path),
                str(tmp_path / "out.png"),
            ]
        )
    assert exc.value.code == 2
