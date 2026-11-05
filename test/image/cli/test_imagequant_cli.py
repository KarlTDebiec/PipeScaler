#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for library-based PNG quantization through the image CLI."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from pipescaler.image.cli import ImageProcessorsCli
from pipescaler.image.cli.processors import ImagequantCli


@pytest.mark.parametrize("skip_if_larger", [False, True])
def test_dispatch_and_size_selection(tmp_path: Path, skip_if_larger: bool):
    """Dispatch library quantization and honor size selection for a tiny PNG.

    Arguments:
        tmp_path: temporary test directory
        skip_if_larger: whether the larger paletted output should be rejected
    """
    input_path = tmp_path / "input with spaces.png"
    output_path = tmp_path / "output with spaces.png"
    Image.new("RGB", (1, 1), (32, 64, 96)).save(input_path, optimize=True)
    arguments = [
        "imagequant",
        "--max-colors",
        "16",
        "--min-quality",
        "0",
        "--max-quality",
        "100",
        "--dithering-level",
        "0.5",
    ]
    if not skip_if_larger:
        arguments.append("--no-skip-if-larger")

    ImageProcessorsCli.main([*arguments, str(input_path), str(output_path)])

    assert ImageProcessorsCli.processors()["imagequant"] is ImagequantCli
    with Image.open(output_path) as output:
        assert output.mode == ("RGB" if skip_if_larger else "P")
        assert output.convert("RGB").getpixel((0, 0)) == (32, 64, 96)
    if skip_if_larger:
        assert output_path.read_bytes() == input_path.read_bytes()


@pytest.mark.parametrize(
    ("option", "value"),
    [
        ("--max-colors", "1"),
        ("--max-colors", "257"),
        ("--min-quality", "-1"),
        ("--max-quality", "101"),
        ("--dithering-level", "nan"),
        ("--dithering-level", "inf"),
        ("--dithering-level", "1.1"),
    ],
)
def test_invalid_arguments(
    tmp_path: Path, option: str, value: str, capsys: pytest.CaptureFixture[str]
):
    """Reject invalid numeric settings before writing output.

    Arguments:
        tmp_path: temporary test directory
        option: numeric option being tested
        value: invalid numeric argument
        capsys: captured command output
    """
    input_path = tmp_path / "input.png"
    output_path = tmp_path / "output.png"
    Image.new("RGB", (2, 2)).save(input_path)

    with pytest.raises(SystemExit) as exc:
        ImagequantCli.main([option, value, str(input_path), str(output_path)])

    assert exc.value.code == 2
    assert f"argument {option}:" in capsys.readouterr().err
    assert not output_path.exists()
