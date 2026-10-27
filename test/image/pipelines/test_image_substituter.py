#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests image substitution."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from pipescaler.image.core.pipelines import PipeImage
from pipescaler.image.pipelines.image_substituter import ImageSubstituter


def test_match_input_mode_preserves_source_for_later_substitution(tmp_path: Path):
    """Converts each substitute in memory without changing its source file.

    Arguments:
        tmp_path: temporary directory for the replacement image
    """
    replacement_path = tmp_path / "sample.png"
    Image.new("RGB", (1, 1), (255, 0, 0)).save(replacement_path)
    original_bytes = replacement_path.read_bytes()
    substituter = ImageSubstituter(tmp_path)

    grayscale = substituter(PipeImage(image=Image.new("L", (1, 1), 0), name="sample"))
    color = substituter(
        PipeImage(image=Image.new("RGB", (1, 1), (0, 0, 0)), name="sample")
    )

    assert grayscale.image.mode == "L"
    assert grayscale.image.getpixel((0, 0)) == 76
    assert color.image.mode == "RGB"
    assert color.image.getpixel((0, 0)) == (255, 0, 0)
    assert replacement_path.read_bytes() == original_bytes


def test_substitute_without_mode_matching_preserves_original_mode(tmp_path: Path):
    """Returns the source mode and pixels when mode matching is disabled.

    Arguments:
        tmp_path: temporary directory for the replacement image
    """
    replacement_path = tmp_path / "sample.png"
    Image.new("RGB", (1, 1), (12, 34, 56)).save(replacement_path)
    original_bytes = replacement_path.read_bytes()
    substituter = ImageSubstituter(tmp_path, match_input_mode=False)

    result = substituter(PipeImage(image=Image.new("L", (1, 1), 0), name="sample"))

    assert result.image.mode == "RGB"
    assert result.image.getpixel((0, 0)) == (12, 34, 56)
    assert replacement_path.read_bytes() == original_bytes
    with Image.open(replacement_path) as source:
        assert source.mode == "RGB"
