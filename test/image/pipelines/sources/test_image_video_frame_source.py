#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for ImageVideoFrameSource."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import cv2
import numpy as np
import pytest

from pipescaler.image.pipelines.sources import ImageVideoFrameSource


@pytest.fixture
def capture(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Provide an opened capture with two tiny BGR frames and a known count.

    Arguments:
        monkeypatch: capture factory replacement
    """
    capture = MagicMock(spec=cv2.VideoCapture)
    capture.isOpened.return_value = True
    capture.get.return_value = 2.0
    frame = np.array([[[10, 20, 30]]], dtype=np.uint8)
    capture.read.side_effect = [(True, frame), (True, frame), (False, None)]
    monkeypatch.setattr(cv2, "VideoCapture", lambda path: capture)
    return capture


@pytest.fixture
def input_path(tmp_path: Path) -> Path:
    """Provide a file path validated without requiring binary video assets.

    Arguments:
        tmp_path: temporary input directory
    """
    path = tmp_path / "clip.mp4"
    path.touch()
    return path


def test_repr_round_trip(input_path: Path, capture: MagicMock):
    """Recreate the source configuration while closing both owners.

    Arguments:
        input_path: existing video path
        capture: mock capture owned by the source
    """
    with ImageVideoFrameSource(input_path, Path("videos")) as source:
        with eval(repr(source)) as recreated:
            assert recreated.input_path == source.input_path
            assert recreated.location_path == source.location_path


def test_failed_open(input_path: Path, capture: MagicMock):
    """Reject an unopened capture and release it immediately.

    Arguments:
        input_path: existing video path
        capture: mock capture owned by the source
    """
    capture.isOpened.return_value = False
    with pytest.raises(OSError, match="Cannot open video"):
        ImageVideoFrameSource(input_path)
    capture.release.assert_called_once()
    capture.read.assert_not_called()


def test_sequential_frames(input_path: Path, capture: MagicMock):
    """Read sequentially, convert BGR, and retain frame names and locations.

    Arguments:
        input_path: existing video path
        capture: mock capture owned by the source
    """
    source = ImageVideoFrameSource(input_path, Path("videos"))
    frames = list(source)
    assert [frame.name for frame in frames] == ["000001", "000002"]
    assert all(frame.location == Path("videos/clip_mp4") for frame in frames)
    assert frames[0].image.getpixel((0, 0)) == (30, 20, 10)
    assert source.index == 2
    capture.set.assert_not_called()
    capture.release.assert_called_once()
    with pytest.raises(StopIteration):
        next(source)
    assert capture.read.call_count == 3


@pytest.mark.parametrize("count", [0.0, -1.0, float("nan"), float("inf"), 1.5])
def test_unknown_count(input_path: Path, capture: MagicMock, count: float):
    """Decode through EOF when the backend cannot provide a usable count.

    Arguments:
        input_path: existing video path
        capture: mock capture owned by the source
        count: unusable reported frame count
    """
    capture.get.return_value = count
    source = ImageVideoFrameSource(input_path)
    assert source.length is None
    assert len(list(source)) == 2
    capture.release.assert_called_once()


def test_underreported_count(input_path: Path, capture: MagicMock):
    """Continue reading past a smaller reported frame count.

    Arguments:
        input_path: existing video path
        capture: mock capture owned by the source
    """
    capture.get.return_value = 1.0
    assert len(list(ImageVideoFrameSource(input_path))) == 2
    capture.release.assert_called_once()


@pytest.mark.parametrize("decoded", [0, 1])
def test_premature_decode_failure(input_path: Path, capture: MagicMock, decoded: int):
    """Report failed initial or truncated decoding and release the capture.

    Arguments:
        input_path: existing video path
        capture: mock capture owned by the source
        decoded: number of frames decoded before failure
    """
    frame = np.zeros((1, 1, 3), dtype=np.uint8)
    capture.read.side_effect = [(True, frame)] * decoded + [(False, None)]
    source = ImageVideoFrameSource(input_path)
    for _ in range(decoded):
        next(source)
    with pytest.raises(OSError, match=f"Cannot decode frame {decoded + 1} of 2"):
        next(source)
    capture.release.assert_called_once()
    with pytest.raises(StopIteration):
        next(source)


def test_missing_frame(input_path: Path, capture: MagicMock):
    """Reject a backend claiming success without returning an image.

    Arguments:
        input_path: existing video path
        capture: mock capture owned by the source
    """
    capture.read.side_effect = [(True, None)]
    with pytest.raises(OSError, match="Decoder returned no frame"):
        next(ImageVideoFrameSource(input_path))
    capture.release.assert_called_once()


def test_decode_exception(input_path: Path, capture: MagicMock):
    """Preserve decoder exceptions while releasing the capture.

    Arguments:
        input_path: existing video path
        capture: mock capture owned by the source
    """
    capture.read.side_effect = cv2.error("decode failed")
    with pytest.raises(cv2.error, match="decode failed"):
        next(ImageVideoFrameSource(input_path))
    capture.release.assert_called_once()


def test_metadata_exception(input_path: Path, capture: MagicMock):
    """Release an opened capture if metadata lookup fails.

    Arguments:
        input_path: existing video path
        capture: mock capture owned by the source
    """
    capture.get.side_effect = cv2.error("metadata failed")
    with pytest.raises(cv2.error, match="metadata failed"):
        ImageVideoFrameSource(input_path)
    capture.release.assert_called_once()


def test_early_close(input_path: Path, capture: MagicMock):
    """Make close idempotent and prevent further reads or reentry.

    Arguments:
        input_path: existing video path
        capture: mock capture owned by the source
    """
    source = ImageVideoFrameSource(input_path)
    next(source)
    source.close()
    source.close()
    capture.release.assert_called_once()
    with pytest.raises(StopIteration):
        next(source)
    with pytest.raises(ValueError, match="closed video frame source"):
        with source:
            pass
    assert capture.read.call_count == 1


def test_context_exception(input_path: Path, capture: MagicMock):
    """Release a partially consumed capture without swallowing caller errors.

    Arguments:
        input_path: existing video path
        capture: mock capture owned by the source
    Raises:
        RuntimeError: if simulated frame processing fails
    """
    with pytest.raises(RuntimeError, match="processing failed"):
        with ImageVideoFrameSource(input_path) as source:
            next(source)
            raise RuntimeError("processing failed")
    capture.release.assert_called_once()
    assert capture.read.call_count == 1


def test_unknown_count_empty(input_path: Path, capture: MagicMock):
    """Treat an immediate failed read as EOF when no frame count is available.

    Arguments:
        input_path: existing video path
        capture: mock capture owned by the source
    """
    capture.get.return_value = 0.0
    capture.read.side_effect = [(False, None)]
    assert list(ImageVideoFrameSource(input_path)) == []
    capture.release.assert_called_once()


def test_context_early_exit(input_path: Path, capture: MagicMock):
    """Release the capture when a consumer leaves the context before EOF.

    Arguments:
        input_path: existing video path
        capture: mock capture owned by the source
    """
    with ImageVideoFrameSource(input_path) as source:
        for frame in source:
            assert frame.name == "000001"
            break
    capture.release.assert_called_once()
    assert capture.read.call_count == 1
