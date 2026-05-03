#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Yields images from a video file."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import cv2
from PIL import Image

from pipescaler.common.validation import val_input_path
from pipescaler.image.core.pipelines import ImageSource, PipeImage

__all__ = ["ImageVideoFrameSource"]


class ImageVideoFrameSource(ImageSource):
    """Yields images from a video file."""

    def __init__(
        self,
        input_path: Path | str,
        location_path: Path | None = None,
        **kwargs: Any,
    ):
        """Initialize.

        Arguments:
            input_path: Video file from which to yield images
            location_path: Path relative to parent directory
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        self.input_path = val_input_path(input_path)
        """Path to video file"""
        self.location_path = location_path
        """Path relative to parent directory"""
        self.cap = cv2.VideoCapture(str(self.input_path))
        """Video capture"""
        self.length = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        """Number of frames in video"""
        self.index = 0
        """Index of next frame to be read"""

    def __repr__(self) -> str:
        """Representation."""
        input_path = f"Path({str(self.input_path)!r})"
        location_path = repr(self.location_path)
        if self.location_path is not None:
            location_path = f"Path({str(self.location_path)!r})"
        return (
            f"{self.__class__.__name__}(input_path={input_path}, "
            f"location_path={location_path})"
        )

    def __next__(self) -> PipeImage:
        """Get next image from video."""
        if self.index < self.length:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.index)
            _, frame = self.cap.read()
            self.index += 1
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            location_path = Path(
                f"{self.input_path.stem}_{self.input_path.suffix.lstrip('.')}"
            )
            if self.location_path:
                location_path = self.location_path / location_path
            return PipeImage(
                image=img,
                name=f"{self.index:06d}",
                location_path=location_path,
            )

        self.cap.release()
        raise StopIteration()
