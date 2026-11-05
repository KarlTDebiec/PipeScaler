#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for processor command-line interfaces."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from pipescaler.common.cli import CommandLineInterface
from pipescaler.common.testing import run_cli_with_args
from pipescaler.image.cli.processors import (
    CropCli,
    ExpandCli,
    HeightToNormalCli,
    ModeCli,
    ResizeCli,
    SharpenCli,
    SolidColorCli,
    ThresholdCli,
    XbrzCli,
)
from pipescaler.testing.file import get_test_input_path


@pytest.mark.parametrize(
    ("cli", "args", "mode", "expected"),
    [
        (CropCli, ["--pixels", "1", "1", "1", "1"], "RGB", ((3, 5), "RGB")),
        (ExpandCli, ["--pixels", "1", "1", "1", "1"], "RGB", ((7, 9), "RGB")),
        (HeightToNormalCli, ["--sigma", "1.0"], "L", ((5, 7), "RGB")),
        (ModeCli, ["--mode", "L"], "RGB", ((5, 7), "L")),
        (ResizeCli, ["--scale", "2"], "RGB", ((10, 14), "RGB")),
        (SharpenCli, [], "RGB", ((5, 7), "RGB")),
        (SolidColorCli, ["--scale", "2"], "RGB", ((10, 14), "RGB")),
        (ThresholdCli, ["--threshold", "64", "--denoise"], "L", ((5, 7), "1")),
        (XbrzCli, ["--scale", "2"], "RGB", ((10, 14), "RGB")),
    ],
)
def test_processor_writes_image(
    cli: type[CommandLineInterface],
    args: list[str],
    mode: str,
    expected: tuple[tuple[int, int], str],
    tmp_path: Path,
):
    """Execute each processor adapter and inspect its saved output.

    Arguments:
        cli: processor command to execute
        args: operation arguments
        mode: input image mode
        expected: saved dimensions and image mode
        tmp_path: temporary image directory
    """
    input_path = tmp_path / "input.png"
    output_path = tmp_path / "output.png"
    image = Image.fromarray(np.arange(35, dtype=np.uint8).reshape(7, 5) * 7)
    image.convert(mode).save(input_path)

    cli.main([*args, str(input_path), str(output_path)])

    with Image.open(output_path) as output:
        output.load()
        assert (output.size, output.mode) == expected


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


@pytest.mark.parametrize(
    ("threshold", "expected"),
    [(1, [0, 0, 255, 255, 255, 255]), (244, [0, 0, 0, 0, 255, 255])],
)
def test_threshold_cli_accepts_processor_boundaries(
    threshold: int, expected: list[int], tmp_path: Path
):
    """Execute threshold CLI at the existing processor bounds.

    Arguments:
        threshold: grayscale cutoff value
        expected: expected output pixels
        tmp_path: temporary directory
    """
    input_path = tmp_path / "input.png"
    output_path = tmp_path / "output.png"
    Image.fromarray(np.array([[0, 1, 2, 244, 245, 255]], dtype=np.uint8)).save(
        input_path
    )

    run_cli_with_args(
        ThresholdCli,
        f"--threshold {threshold} {input_path} {output_path}",
    )

    with Image.open(output_path) as output_image:
        assert output_image.mode == "1"
        assert np.array(output_image.convert("L")).flatten().tolist() == expected


@pytest.mark.parametrize("threshold", [-1, 0, 245, 255, 256])
def test_threshold_cli_rejects_out_of_range_values(
    threshold: int, tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    """Reject unsupported thresholds before executing the processor.

    Arguments:
        threshold: unsupported threshold
        tmp_path: temporary directory for output
        capsys: captured command output
    """
    output_path = tmp_path / "output.png"
    with pytest.raises(SystemExit) as exc:
        ThresholdCli.main(
            [
                "--threshold",
                str(threshold),
                str(get_test_input_path("L")),
                str(output_path),
            ]
        )
    assert exc.value.code == 2
    assert "argument --threshold:" in capsys.readouterr().err
    assert not output_path.exists()


@pytest.mark.parametrize("scale", ["0", "-1", "nan", "inf", "-inf"])
def test_resize_cli_rejects_invalid_scales(
    scale: str, tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    """Reject invalid scales with an argument error before dispatch.

    Arguments:
        scale: invalid scale argument
        tmp_path: temporary directory for output
        capsys: captured command output
    """
    output_path = tmp_path / "output.png"
    with pytest.raises(SystemExit) as exc:
        ResizeCli.main(
            ["--scale", scale, str(get_test_input_path("L")), str(output_path)]
        )
    assert exc.value.code == 2
    assert "argument --scale:" in capsys.readouterr().err
    assert not output_path.exists()
