#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for decoding numbered images with capture metadata and cleanup."""

from __future__ import annotations

from pathlib import Path

import cv2
import pytest

from pipescaler.common.exceptions import NotAFileError
from pipescaler.video.core.image_sequence_capture import ImageSequenceCapture
from pipescaler.video.core.video_input import VideoInput
from test.scripts.generate_video_inputs import write_image_sequence


def test_empty_or_corrupt_first_frame(tmp_path: Path):
    """Reject captures without a decodable first frame.

    Arguments:
        tmp_path: temporary input directory
    """
    with pytest.raises(ValueError, match="at least one"):
        ImageSequenceCapture(())
    frame_path = tmp_path / "000001.png"
    frame_path.write_text("not an image", encoding="utf-8")
    with pytest.raises(OSError, match="000001.png"):
        ImageSequenceCapture((frame_path,))


def test_metadata_reading_and_release(tmp_path: Path):
    """Read all frames in BGR order and close idempotently after EOF.

    Arguments:
        tmp_path: temporary input directory
    """
    input_path = write_image_sequence(tmp_path)
    capture = VideoInput(input_path).open_capture()
    assert capture.isOpened()
    assert capture.get(cv2.CAP_PROP_FRAME_COUNT) == 3
    assert capture.get(cv2.CAP_PROP_FRAME_WIDTH) == 16
    assert capture.get(cv2.CAP_PROP_FRAME_HEIGHT) == 12
    assert capture.get(cv2.CAP_PROP_FPS) == 0
    for index in (7, 8, 9):
        success, frame = capture.read()
        assert success and frame is not None
        assert frame[0, 0].tolist() == [30, 20, index]
        assert capture.get(cv2.CAP_PROP_POS_FRAMES) == index - 6
    assert capture.read() == (False, None)
    capture.release()
    capture.release()
    assert not capture.isOpened()
    assert capture.get(cv2.CAP_PROP_FRAME_COUNT) == 0
    assert capture.read() == (False, None)


def test_validates_concrete_frame_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Normalize direct capture inputs and reject missing files or directories.

    Arguments:
        tmp_path: temporary input directory
        monkeypatch: working directory replacement
    """
    write_image_sequence(tmp_path)
    monkeypatch.chdir(tmp_path)
    capture = ImageSequenceCapture((Path("000007.png"),))
    try:
        assert capture.read()[0]
    finally:
        capture.release()
    with pytest.raises(FileNotFoundError, match="missing.png"):
        ImageSequenceCapture((tmp_path / "missing.png",))
    with pytest.raises(NotAFileError, match="not a file"):
        ImageSequenceCapture((tmp_path,))


@pytest.mark.parametrize("failure", ["corrupt", "missing", "directory", "dimensions"])
def test_later_frame_failure(tmp_path: Path, failure: str):
    """Identify failed frames and release instead of silently ending playback.

    Arguments:
        tmp_path: temporary input directory
        failure: decoding failure injected after the sequence is resolved
    """
    input_path = write_image_sequence(tmp_path)
    capture = VideoInput(input_path).open_capture()
    frame_path = tmp_path / "000008.png"
    if failure == "corrupt":
        frame_path.write_text("not an image", encoding="utf-8")
    elif failure == "missing":
        frame_path.unlink()
    elif failure == "directory":
        frame_path.unlink()
        frame_path.mkdir()
    else:
        write_image_sequence(tmp_path, indices=(8,), size=(2, 2))
    assert capture.read()[0]
    with pytest.raises(OSError, match="000008.png"):
        capture.read()
    assert not capture.isOpened()
