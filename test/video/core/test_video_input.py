#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for concrete video files and numbered image-sequence specifications."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import cv2
import pytest

from pipescaler.common.exceptions import NotAFileError
from pipescaler.common.validation import val_input_path
from pipescaler.video.core.video_input import VideoInput
from test.scripts.generate_video_inputs import write_image_sequence


def test_concrete_paths(tmp_path: Path):
    """Preserve strict file validation and allow literal percent-bearing files.

    Arguments:
        tmp_path: temporary input directory
    """
    input_path = tmp_path / "literal%d.mp4"
    input_path.touch()
    video_input = VideoInput(input_path)
    assert video_input.input_path == input_path
    assert video_input.frame_paths is None
    with pytest.raises(FileNotFoundError):
        VideoInput(tmp_path / "missing.mp4")
    with pytest.raises(NotAFileError):
        VideoInput(tmp_path)


def test_failed_video_open_releases_capture(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Release file captures rejected while opening the input.

    Arguments:
        tmp_path: temporary input directory
        monkeypatch: OpenCV factory replacement
    """
    input_path = tmp_path / "broken.mp4"
    input_path.touch()
    capture = MagicMock(spec=cv2.VideoCapture)
    capture.isOpened.return_value = False
    monkeypatch.setattr(cv2, "VideoCapture", lambda path: capture)

    with pytest.raises(OSError, match="Cannot open video"):
        VideoInput(input_path).open_capture()
    capture.release.assert_called_once()


def test_pattern_literals_and_padding(tmp_path: Path):
    """Treat surrounding regex characters literally and enforce printf padding.

    Arguments:
        tmp_path: temporary input directory
    """
    pattern = "frame[0].%02d.png"
    input_path = write_image_sequence(tmp_path, pattern, (9, 10))
    (tmp_path / "frame[0].9.png").touch()
    (tmp_path / "frame0.08.png").touch()

    assert VideoInput(input_path).frame_paths == (
        tmp_path / "frame[0].09.png",
        tmp_path / "frame[0].10.png",
    )


@pytest.mark.parametrize("pattern", ["%06d.png", "%06d/image.png", "missing/%d.png"])
def test_empty_sequence(tmp_path: Path, pattern: str):
    """Report no matching frames, including when the parent does not exist.

    Arguments:
        tmp_path: temporary input directory
        pattern: sequence without any matching frame files
    """
    with pytest.raises(FileNotFoundError, match="No image-sequence frames"):
        VideoInput(tmp_path / pattern)


@pytest.mark.parametrize(
    "pattern", ["%s.png", "%00d.png", "%0d.png", "%03x.png", "%d/%d.png"]
)
def test_malformed_pattern(tmp_path: Path, pattern: str):
    """Reject unsupported or multiple substitutions before scanning.

    Arguments:
        tmp_path: temporary input directory
        pattern: unsupported input template
    """
    with pytest.raises(ValueError, match="exactly one"):
        VideoInput(tmp_path / pattern)


@pytest.mark.parametrize("pattern", ["%06d.png", "%06d/image.png"])
def test_numbering_gap(tmp_path: Path, pattern: str):
    """Report missing indices instead of truncating the sequence at a gap.

    Arguments:
        tmp_path: temporary input directory
        pattern: flat or nested template
    """
    input_path = write_image_sequence(tmp_path, pattern, (7, 9))
    with pytest.raises(ValueError, match="Missing image-sequence frame 8"):
        VideoInput(input_path)


@pytest.mark.parametrize(
    "pattern", ["%d.png", "%06d.png", "frame_%02d.png", "%06d/image.png"]
)
@pytest.mark.parametrize("start", [0, 9, 99])
def test_sequence_resolution(tmp_path: Path, pattern: str, start: int):
    """Resolve both layouts in numeric order across padding boundaries.

    Arguments:
        tmp_path: temporary input directory
        pattern: supported numbered path template
        start: arbitrary starting index
    """
    input_path = write_image_sequence(
        tmp_path / "frames", pattern, (start + 2, start, start + 1)
    )
    video_input = VideoInput(input_path)

    assert video_input.frame_paths == tuple(
        tmp_path / "frames" / (pattern % index) for index in range(start, start + 3)
    )
    assert video_input.name == "frames"
    assert eval(repr(video_input)).frame_paths == video_input.frame_paths
    with pytest.raises(FileNotFoundError):
        val_input_path(input_path)
