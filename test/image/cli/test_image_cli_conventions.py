#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Contracts shared by image leaf command-line interfaces."""

from __future__ import annotations

from inspect import Parameter, signature
from pathlib import Path
from typing import get_type_hints

import pytest
from PIL import Image

from pipescaler.common import CommandLineInterface
from pipescaler.image.cli import ImageMergersCli, ImageProcessorsCli, ImageSplittersCli
from pipescaler.image.cli.mergers import AlphaMergerCli, PaletteMatchMergerCli
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
from pipescaler.image.cli.splitters import AlphaSplitterCli


@pytest.mark.parametrize(
    ("cli", "has_operation"),
    [
        (CropCli, True),
        (ExpandCli, True),
        (HeightToNormalCli, True),
        (ModeCli, True),
        (ResizeCli, True),
        (SharpenCli, False),
        (SolidColorCli, True),
        (SpandrelCli, False),
        (ThresholdCli, True),
        (XbrzCli, True),
        (AlphaMergerCli, False),
        (PaletteMatchMergerCli, True),
        (AlphaSplitterCli, False),
    ],
)
def test_leaf_help_and_parameter_contract(
    cli: type[CommandLineInterface], has_operation: bool
):
    """Keep role-based help and explicit execution parameters aligned.

    Arguments:
        cli: leaf command to inspect
        has_operation: whether the command has operation settings
    """
    parser = cli.argparser()
    groups = parser._action_groups
    expected = ["input arguments"]
    if has_operation:
        expected.append("operation arguments")
    expected.extend(["output arguments", "additional arguments"])
    assert [group.title for group in groups] == expected
    assert all(group._group_actions for group in groups)
    for group in groups:
        for action in group._group_actions:
            assert all("_" not in option for option in action.option_strings)

    parameters = signature(cli._main).parameters
    parsed_names = {
        action.dest
        for group in groups
        if group.title != "additional arguments"
        for action in group._group_actions
    }
    assert set(parameters) == parsed_names
    assert all(
        parameter.kind is Parameter.KEYWORD_ONLY for parameter in parameters.values()
    )
    annotations = get_type_hints(cli._main)
    assert all(name in annotations for name in parameters)
    assert all(
        annotations[name] is Path for name in parameters if name.endswith("_path")
    )


def test_mode_background_color_through_parent(tmp_path: Path):
    """Apply the hyphenated background option through processor dispatch.

    Arguments:
        tmp_path: temporary image directory
    """
    input_path = tmp_path / "input.png"
    output_path = tmp_path / "output.png"
    Image.new("RGBA", (1, 1), (0, 0, 0, 0)).save(input_path)
    ImageProcessorsCli.main(
        [
            "mode",
            "--mode",
            "RGB",
            "--background-color",
            "#123456",
            str(input_path),
            str(output_path),
        ]
    )
    with Image.open(output_path) as output_image:
        assert output_image.getpixel((0, 0)) == (18, 52, 86)


@pytest.mark.parametrize(
    ("cli", "operation_args", "obsolete_option"),
    [
        (ModeCli, ["--mode", "RGB"], "--background_color"),
        (PaletteMatchMergerCli, ["--local"], "--local_range"),
    ],
)
def test_obsolete_option_spellings_are_rejected(
    cli: type[CommandLineInterface],
    operation_args: list[str],
    obsolete_option: str,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
):
    """Reject removed underscore options instead of retaining aliases.

    Arguments:
        cli: leaf command to parse
        operation_args: valid operation settings
        obsolete_option: removed option spelling
        tmp_path: temporary image directory
        capsys: captured parser diagnostics
    """
    input_path = tmp_path / "input.png"
    Image.new("RGB", (1, 1)).save(input_path)
    paths = [str(input_path)]
    if cli is PaletteMatchMergerCli:
        paths.append(str(input_path))
    paths.append(str(tmp_path / "output.png"))
    with pytest.raises(SystemExit) as exc:
        cli.argparser().parse_args([*operation_args, *paths, obsolete_option, "1"])
    assert exc.value.code == 2
    assert f"unrecognized arguments: {obsolete_option}" in capsys.readouterr().err


def test_alpha_round_trip_through_parents(tmp_path: Path):
    """Preserve image pixels through typed splitter and merger dispatch.

    Arguments:
        tmp_path: temporary image directory
    """
    input_path = tmp_path / "input.png"
    color_path = tmp_path / "color.png"
    alpha_path = tmp_path / "alpha.png"
    output_path = tmp_path / "output.png"
    Image.new("RGBA", (2, 2), (18, 52, 86, 123)).save(input_path)
    ImageSplittersCli.main(
        ["alphasplitter", str(input_path), str(color_path), str(alpha_path)]
    )
    ImageMergersCli.main(
        ["alphamerger", str(color_path), str(alpha_path), str(output_path)]
    )
    with Image.open(output_path) as output_image:
        assert output_image.mode == "RGBA"
        assert output_image.size == (2, 2)
        assert output_image.getpixel((0, 0)) == (18, 52, 86, 123)
