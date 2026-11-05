#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for merger command-line interfaces."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from pipescaler.cli import PipeScalerCli
from pipescaler.image.cli.mergers import (
    PaletteMatchMergerCli,
)
from pipescaler.testing.file import get_test_input_path


@pytest.mark.parametrize("args", [[], ["--local"], ["--local", "--local-range", "2"]])
def test_palette_match_preserves_exact_colors(args: list[str], tmp_path: Path):
    """Wire palette options to a merger that preserves exact reference colors.

    Arguments:
        args: global or local matching options
        tmp_path: temporary image directory
    """
    reference_path = tmp_path / "reference.png"
    target_path = tmp_path / "target.png"
    output_path = tmp_path / "output.png"
    reference = Image.new("RGB", (2, 2))
    for index, color in enumerate(
        [(12, 34, 56), (200, 10, 90), (40, 170, 30), (230, 210, 190)]
    ):
        reference.putpixel((index % 2, index // 2), color)
    target = reference.resize((4, 4), Image.Resampling.NEAREST)
    reference.save(reference_path)
    target.save(target_path)

    PaletteMatchMergerCli.main(
        [
            *args,
            str(reference_path),
            str(target_path),
            str(output_path),
        ]
    )

    with Image.open(output_path) as output:
        assert output.mode == target.mode
        assert output.size == target.size
        assert output.tobytes() == target.tobytes()


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
        PaletteMatchMergerCli.argparser().parse_args(
            [
                "--local-range",
                local_range,
                str(input_path),
                str(input_path),
                str(tmp_path / "out.png"),
            ]
        )
    assert exc.value.code == 2
