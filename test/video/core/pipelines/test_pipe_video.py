#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for unsupported video saving."""

from __future__ import annotations

from pathlib import Path

import cv2
import pytest

from pipescaler.video.core.pipelines import PipeVideo
from pipescaler.video.core.video_input import VideoInput
from test.scripts.generate_video_inputs import write_image_sequence, write_video


@pytest.mark.parametrize("pattern", ["%06d.png", "%06d/image.png"])
def test_image_sequence_input(tmp_path: Path, pattern: str):
    """Retain a sequence specification without presenting it as a concrete file.

    Arguments:
        tmp_path: temporary input directory
        pattern: flat or nested image template
    """
    input_path = write_image_sequence(tmp_path / "frames", pattern)
    video = PipeVideo(path=input_path, location_path=Path("videos"))
    assert video.path is None
    assert video.input_path == input_path
    assert video.name == VideoInput(input_path).name
    assert video.location_name == str(Path("videos") / video.name)
    assert video._video is None
    recreated = eval(repr(video))
    assert recreated.input_path == input_path
    assert recreated.location == video.location
    capture = video.video
    try:
        assert capture.get(cv2.CAP_PROP_FRAME_COUNT) == 3
        assert capture.get(cv2.CAP_PROP_FRAME_WIDTH) == 16
        assert capture.get(cv2.CAP_PROP_FRAME_HEIGHT) == 12
        for index in (7, 8, 9):
            success, frame = capture.read()
            assert success and frame is not None
            assert frame[0, 0].tolist() == [30, 20, index]
        assert capture.read() == (False, None)
    finally:
        capture.release()


def test_video_file_input(tmp_path: Path):
    """Keep concrete-file identity while lazily opening real video captures.

    Arguments:
        tmp_path: temporary input directory
    """
    input_path = write_video(tmp_path / "clip.mp4")
    video = PipeVideo(path=input_path)
    assert video.path == input_path
    assert video.input_path == input_path
    assert video._video is None
    capture = video.video
    try:
        assert capture.isOpened()
        assert capture.get(cv2.CAP_PROP_FRAME_COUNT) == 3
        assert capture.read()[0]
    finally:
        capture.release()


@pytest.mark.parametrize("existing_output", [False, True])
def test_save_preserves_state_and_files(tmp_path: Path, existing_output: bool):
    """Reject saving without changing the source, target, or object path.

    Arguments:
        tmp_path: temporary test directory
        existing_output: whether the output file already exists
    """
    input_path = tmp_path / "input.mp4"
    input_path.write_bytes(b"source video")
    output_path = tmp_path / "new" / "output.mp4"
    if existing_output:
        output_path.parent.mkdir()
        output_path.write_bytes(b"existing output")
    video = PipeVideo(path=input_path)

    with pytest.raises(NotImplementedError, match="video encoding"):
        video.save(output_path)

    assert video.path == input_path
    assert input_path.read_bytes() == b"source video"
    assert video._video is None
    if existing_output:
        assert output_path.read_bytes() == b"existing output"
    else:
        assert not output_path.parent.exists()
