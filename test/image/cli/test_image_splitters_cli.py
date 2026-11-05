#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for splitter command-line interfaces."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from pipescaler.image.cli.splitters import AlphaSplitterCli


def test_splitter_writes_color_and_alpha(tmp_path: Path):
    """Preserve color and opacity in both outputs of the standalone splitter.

    Arguments:
        tmp_path: temporary image directory
    """
    input_path = tmp_path / "input.png"
    color_path = tmp_path / "color.png"
    alpha_path = tmp_path / "alpha.png"
    image = Image.new("RGBA", (2, 1))
    image.putpixel((0, 0), (12, 34, 56, 78))
    image.putpixel((1, 0), (90, 123, 145, 255))
    image.save(input_path)

    AlphaSplitterCli.main([str(input_path), str(color_path), str(alpha_path)])

    with Image.open(color_path) as color, Image.open(alpha_path) as alpha:
        assert color.mode == "RGB"
        assert alpha.mode == "L"
        assert color.size == alpha.size == image.size
        assert color.tobytes() == image.convert("RGB").tobytes()
        assert alpha.tobytes() == image.getchannel("A").tobytes()
