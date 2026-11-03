#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Generate tiny, reproducible video and numbered-image test inputs."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image

__all__ = ["write_image_sequence", "write_video"]


def write_image_sequence(
    dir_path: Path,
    pattern: str = "%06d.png",
    indices: tuple[int, ...] = (7, 8, 9),
    size: tuple[int, int] = (16, 12),
) -> Path:
    """Write color-coded frames in the supplied creation order.

    Arguments:
        dir_path: root directory for generated frames
        pattern: relative printf path with one integer placeholder
        indices: frame numbers and creation order
        size: frame dimensions
    Returns:
        absolute sequence template
    """
    for index in indices:
        frame_path = dir_path / (pattern % index)
        frame_path.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", size, (index % 256, 20, 30)).save(frame_path)
    return (dir_path / pattern).resolve()


def write_video(file_path: Path) -> Path:
    """Write a three-frame MP4 using the OpenCV MPEG-4 encoder.

    Arguments:
        file_path: destination for the generated MP4
    Returns:
        absolute video path
    Raises:
        OSError: if the video encoder cannot be opened
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(
        str(file_path), cv2.VideoWriter.fourcc(*"mp4v"), 24, (16, 12)
    )
    try:
        if not writer.isOpened():
            raise OSError("Cannot open the MP4 test encoder.")
        for index in range(3):
            writer.write(np.full((12, 16, 3), index * 60, dtype=np.uint8))
    finally:
        writer.release()
    return file_path.resolve()
