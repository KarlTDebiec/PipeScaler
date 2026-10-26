#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for VideoDirectoryTerminus."""

from __future__ import annotations

from os import utime
from pathlib import Path

from pipescaler.video.core.pipelines import PipeVideo
from pipescaler.video.pipelines.termini import VideoDirectoryTerminus


def _set_mtime(path: Path, timestamp: float) -> None:
    """Set both file timestamps to a deterministic value.

    Arguments:
        path: file to update
        timestamp: timestamp to set
    """
    utime(path, (timestamp, timestamp))


def test_writes_new_video(tmp_path: Path):
    """Copy a new input video to the output directory.

    Arguments:
        tmp_path: temporary test directory
    """
    input_path = tmp_path / "input.mp4"
    input_path.write_bytes(b"input bytes")
    terminus = VideoDirectoryTerminus(tmp_path / "output")

    terminus(PipeVideo(path=input_path))

    output_path = tmp_path / "output" / "input.mp4"
    assert output_path.read_bytes() == b"input bytes"
    assert "input.mp4" in terminus.observed_files


def test_replaces_older_video(tmp_path: Path):
    """Replace an output whose timestamp is older than the input.

    Arguments:
        tmp_path: temporary test directory
    """
    input_path = tmp_path / "input.mp4"
    output_path = tmp_path / "output" / "input.mp4"
    output_path.parent.mkdir()
    input_path.write_bytes(b"new input")
    output_path.write_bytes(b"old output")
    _set_mtime(input_path, 200)
    _set_mtime(output_path, 100)
    terminus = VideoDirectoryTerminus(output_path.parent)

    terminus(PipeVideo(path=input_path))

    assert output_path.read_bytes() == b"new input"


def test_preserves_equal_timestamp_video(tmp_path: Path):
    """Preserve existing output when timestamps are equal.

    Arguments:
        tmp_path: temporary test directory
    """
    input_path = tmp_path / "input.mp4"
    output_path = tmp_path / "output" / "input.mp4"
    output_path.parent.mkdir()
    input_path.write_bytes(b"different input")
    output_path.write_bytes(b"existing output")
    _set_mtime(input_path, 200)
    _set_mtime(output_path, 200)
    terminus = VideoDirectoryTerminus(output_path.parent)

    terminus(PipeVideo(path=input_path))

    assert output_path.read_bytes() == b"existing output"
    assert output_path.stat().st_mtime == 200


def test_preserves_newer_timestamp_video(tmp_path: Path):
    """Preserve existing output when its timestamp is newer.

    Arguments:
        tmp_path: temporary test directory
    """
    input_path = tmp_path / "input.mp4"
    output_path = tmp_path / "output" / "input.mp4"
    output_path.parent.mkdir()
    input_path.write_bytes(b"input")
    output_path.write_bytes(b"newer output")
    _set_mtime(input_path, 100)
    _set_mtime(output_path, 200)
    terminus = VideoDirectoryTerminus(output_path.parent)

    terminus(PipeVideo(path=input_path))

    assert output_path.read_bytes() == b"newer output"
    assert output_path.stat().st_mtime == 200


def test_handles_input_and_output_as_same_path(tmp_path: Path):
    """Leave an input unchanged when it is already at its output path.

    Arguments:
        tmp_path: temporary test directory
    """
    input_path = tmp_path / "input.mp4"
    input_path.write_bytes(b"input bytes")
    _set_mtime(input_path, 200)
    terminus = VideoDirectoryTerminus(tmp_path)

    terminus(PipeVideo(path=input_path))

    assert input_path.read_bytes() == b"input bytes"
    assert input_path.stat().st_mtime == 200
    assert "input.mp4" in terminus.observed_files


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
