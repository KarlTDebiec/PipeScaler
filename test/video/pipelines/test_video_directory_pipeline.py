#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test discovering, routing, and copying real video files."""

from __future__ import annotations

from pathlib import Path

from pipescaler.video.pipelines.sorters import VideoAspectRatioSorter
from pipescaler.video.pipelines.sources import VideoDirectorySource
from pipescaler.video.pipelines.termini import VideoDirectoryTerminus
from test.scripts.generate_video_inputs import write_video


def test_copy_video_matching_aspect_ratio(tmp_path: Path):
    """Route a matching clip and preserve its relative path and contents.

    Arguments:
        tmp_path: temporary input and output directory
    """
    input_dir_path = tmp_path / "input"
    root_path = write_video(input_dir_path / "square.mp4", size=(16, 16))
    nested_path = write_video(input_dir_path / "nested" / "four-three.mp4")
    sorter = VideoAspectRatioSorter(four_three=1.33)
    output_dir_path = tmp_path / "output"
    terminus = VideoDirectoryTerminus(output_dir_path / "four_three")

    videos = list(VideoDirectorySource(input_dir_path))
    assert len(videos) == 2
    routes = {}
    for video in videos:
        capture = video.video
        try:
            outlet = sorter(video)
        finally:
            capture.release()
        routes[video.path] = (Path(video.location_name), outlet)
        if outlet == "four_three":
            terminus(video)

    assert routes == {
        root_path: (Path("square"), None),
        nested_path: (Path("nested/four-three"), "four_three"),
    }
    output_path = output_dir_path / "four_three" / "nested" / "four-three.mp4"
    assert {path for path in output_dir_path.rglob("*") if path.is_file()} == {
        output_path
    }
    assert output_path.read_bytes() == nested_path.read_bytes()
