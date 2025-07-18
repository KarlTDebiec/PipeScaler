#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Yields images from a video file."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import cv2
from PIL import Image

from pipescaler.common.validation import validate_input_file
from pipescaler.image.core.pipelines import ImageSource, PipeImage


class ImageVideoFrameSource(ImageSource):
    """Yields images from a video file."""

    def __init__(
        self,
        input_path: Path | str,
        location: Path | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize.

        Arguments:
            input_path: Video file from which to yield images
            location: Path relative to parent directory
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        self.input_path = validate_input_file(input_path)
        """Path to video file"""
        self.location = location
        """Path relative to parent directory"""
        self.cap = cv2.VideoCapture(str(self.input_path))
        """Video capture"""
        self.length = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        """Number of frames in video"""
        self.index = 0
        """Index of next frame to be read"""

    def __next__(self) -> PipeImage:
        """Get next image from video."""
        if self.index < self.length:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.index)
            _, frame = self.cap.read()
            self.index += 1
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            location = Path(
                f"{self.input_path.stem}_{self.input_path.suffix.lstrip('.')}"
            )
            if self.location:
                location = self.location / location
            return PipeImage(
                image=img,
                name=f"{self.index:06d}",
                location=location,
            )

        self.cap.release()
        raise StopIteration()
