#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for VideoDirectoryTerminus."""

from __future__ import annotations

from pathlib import Path

from pipescaler.video.core.pipelines import PipeVideo
from pipescaler.video.pipelines.termini import VideoDirectoryTerminus


def test_preserves_dotted_names(tmp_path: Path):
    """Keep dotted video stems and copied file content distinct.

    Arguments:
        tmp_path: temporary test directory
    """
    terminus = VideoDirectoryTerminus(tmp_path / "output")
    contents = {
        "video.one": b"first video content",
        "video.two": b"second video content",
    }
    location_path = Path("nested.directory")
    for name, content in contents.items():
        input_path = tmp_path / f"{name}.mp4"
        input_path.write_bytes(content)
        terminus(PipeVideo(path=input_path, location_path=location_path))

    terminus.purge_unrecognized_files()
    output_dir_path = terminus.dir_path / location_path
    assert {path.name for path in output_dir_path.iterdir()} == {
        "video.one.mp4",
        "video.two.mp4",
    }
    for name, content in contents.items():
        assert (output_dir_path / f"{name}.mp4").read_bytes() == content
