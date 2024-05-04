#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Yields images from a video file."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import cv2
from PIL import Image

from pipescaler.common import PathLike, validate_input_file
from pipescaler.image.core.pipelines import ImageSource, PipeImage


class ImageVideoFrameSource(ImageSource):
    """Yields images from a video file."""

    def __init__(
        self,
        infile: PathLike,
        location: Path | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize.

        Arguments:
            infile: Video file from which to yield images
            location: Path relative to parent directory
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        self.infile = validate_input_file(infile)
        """Path to video file"""
        self.location = location
        """Path relative to parent directory"""
        self.cap = cv2.VideoCapture(str(self.infile))
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
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            location = Path(f"{self.infile.stem}_{self.infile.suffix.lstrip('.')}")
            if self.location:
                location = self.location / location
            return PipeImage(
                image=image,
                name=f"{self.index:06d}",
                location=location,
            )

        self.cap.release()
        raise StopIteration()
