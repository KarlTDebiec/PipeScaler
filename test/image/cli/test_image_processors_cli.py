#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for processor command-line interfaces."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from inspect import getfile
from io import StringIO
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from pipescaler.common import CommandLineInterface
from pipescaler.common.file import get_temp_directory_path, get_temp_file_path
from pipescaler.common.testing import run_cli_with_args
from pipescaler.image.cli import ImageProcessorsCli
from pipescaler.image.cli.processors import (
    CropCli,
    ExpandCli,
    HeightToNormalCli,
    ModeCli,
    ResizeCli,
    SharpenCli,
    SolidColorCli,
    SpandrelCli,
    ThresholdCli,
    XbrzCli,
)
from pipescaler.testing.file import get_test_input_path


@pytest.mark.parametrize(
    ("cli", "args", "input_filename"),
    [
        (CropCli, "--pixels 4 4 4 4", "RGB"),
        (ExpandCli, "--pixels 8 8 8 8", "RGB"),
        (HeightToNormalCli, "--sigma 1.0", "L"),
        (ModeCli, "--mode L", "RGB"),
        (ResizeCli, "--scale 2", "RGB"),
        (SharpenCli, "", "RGB"),
        (SolidColorCli, "--scale 2", "RGB"),
        (ThresholdCli, "--threshold 64 --denoise", "L"),
        (XbrzCli, "--scale 2", "RGB"),
    ],
)
def test(cli: type[CommandLineInterface], args: str, input_filename: str):
    """Test processor CLI with various input files and arguments.

    Arguments:
        cli: The command-line interface class to test
        args: Command-line arguments string
        input_filename: Input image filename
    """
    input_path = get_test_input_path(input_filename)

    with get_temp_file_path(".png") as output_path:
        run_cli_with_args(cli, f"{args} {input_path} {output_path}")


@pytest.mark.parametrize(
    "commands",
    [
        (CropCli,),
        (ExpandCli,),
        (HeightToNormalCli,),
        (ModeCli,),
        (ResizeCli,),
        (SharpenCli,),
        (SolidColorCli,),
        (SpandrelCli,),
        (ThresholdCli,),
        (XbrzCli,),
        (ImageProcessorsCli,),
        (ImageProcessorsCli, CropCli),
        (ImageProcessorsCli, ExpandCli),
        (ImageProcessorsCli, HeightToNormalCli),
        (ImageProcessorsCli, ModeCli),
        (ImageProcessorsCli, ResizeCli),
        (ImageProcessorsCli, SharpenCli),
        (ImageProcessorsCli, SolidColorCli),
        (ImageProcessorsCli, SpandrelCli),
        (ImageProcessorsCli, ThresholdCli),
        (ImageProcessorsCli, XbrzCli),
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
        (CropCli,),
        (ExpandCli,),
        (HeightToNormalCli,),
        (ModeCli,),
        (ResizeCli,),
        (SharpenCli,),
        (SolidColorCli,),
        (SpandrelCli,),
        (ThresholdCli,),
        (XbrzCli,),
        (ImageProcessorsCli,),
        (ImageProcessorsCli, CropCli),
        (ImageProcessorsCli, ExpandCli),
        (ImageProcessorsCli, HeightToNormalCli),
        (ImageProcessorsCli, ModeCli),
        (ImageProcessorsCli, ResizeCli),
        (ImageProcessorsCli, SharpenCli),
        (ImageProcessorsCli, SolidColorCli),
        (ImageProcessorsCli, SpandrelCli),
        (ImageProcessorsCli, ThresholdCli),
        (ImageProcessorsCli, XbrzCli),
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


def test_spandrel_cli_registration_and_parsing():
    """Test that SpandrelCli is registered and parses its model path."""
    assert ImageProcessorsCli.processors()["spandrel"] is SpandrelCli

    input_path = get_test_input_path("RGB")
    with get_temp_file_path(".pth") as model_input_path:
        with get_temp_directory_path() as output_dir_path:
            model_input_path.touch()
            output_path = output_dir_path / "output.png"

            parsed_args = ImageProcessorsCli.argparser().parse_args(
                [
                    "spandrel",
                    "--model-input-path",
                    str(model_input_path),
                    str(input_path),
                    str(output_path),
                ]
            )

    assert parsed_args.processor == "spandrel"
    assert parsed_args.model_input_path == model_input_path.resolve()
    assert parsed_args.input_file == input_path
    assert parsed_args.output_file == output_path.resolve()


@pytest.mark.parametrize(
    ("cli", "args", "expected_size"),
    [
        (CropCli, "--pixels 0 0 1 1", (2, 2)),
        (ExpandCli, "--pixels 0 1 0 0", (3, 4)),
    ],
)
def test_zero_pixel_sides_execute(
    cli: type[CommandLineInterface],
    args: str,
    expected_size: tuple[int, int],
    tmp_path: Path,
):
    """Run crop and expand with a zero-valued side and inspect output pixels.

    Arguments:
        cli: command-line interface to execute
        args: command-line operation arguments
        expected_size: expected output image dimensions
        tmp_path: temporary directory
    """
    input_path = tmp_path / "input.png"
    output_path = tmp_path / "output.png"
    Image.new("L", (3, 3), 128).save(input_path)

    run_cli_with_args(cli, f"{args} {input_path} {output_path}")

    with Image.open(output_path) as output_image:
        assert output_image.size == expected_size
        assert (
            np.array(output_image).tolist()
            == np.full(
                (expected_size[1], expected_size[0]), 128, dtype=np.uint8
            ).tolist()
        )


@pytest.mark.parametrize(("threshold", "expected"), [(0, [0, 255]), (255, [0, 0])])
def test_threshold_cli_accepts_8_bit_boundaries(
    threshold: int, expected: list[int], tmp_path: Path
):
    """Execute threshold CLI at the valid grayscale endpoints.

    Arguments:
        threshold: grayscale cutoff value
        expected: expected output pixels
        tmp_path: temporary directory
    """
    input_path = tmp_path / "input.png"
    output_path = tmp_path / "output.png"
    Image.fromarray(np.array([[0, 255]], dtype=np.uint8)).save(input_path)

    run_cli_with_args(
        ThresholdCli,
        f"--threshold {threshold} {input_path} {output_path}",
    )

    with Image.open(output_path) as output_image:
        assert np.array(output_image).flatten().tolist() == expected
