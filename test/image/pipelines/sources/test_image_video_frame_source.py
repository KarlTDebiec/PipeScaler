#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for ImageVideoFrameSource."""

from __future__ import annotations

from pathlib import Path

from pipescaler.common.file import get_temp_file_path
from pipescaler.image.pipelines.sources import ImageVideoFrameSource


def test_repr_round_trip():
    """Test ImageVideoFrameSource repr round-trip recreation."""
    with get_temp_file_path(".mp4") as input_path:
        input_path.touch()
        source = ImageVideoFrameSource(
            input_path=input_path,
            location=Path("videos"),
        )
        recreated = eval(repr(source))
        assert recreated.input_path == source.input_path
        assert recreated.location == source.location
