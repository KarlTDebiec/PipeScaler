#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Yields images from a video file."""
from __future__ import annotations

from typing import Any

import cv2

from pipescaler.common import PathLike, validate_input_file
from pipescaler.core.pipelines import Source


class VideoSource(Source):
    """Yields images from a video file."""

    def __init__(
        self,
        infile: PathLike,
        **kwargs: Any,
    ) -> None:
        """Initialize.

        Arguments:
            infile: Video file from which to yield images
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Count number of frames in video file
        self.infile = validate_input_file(infile)
        self.cap = cv2.VideoCapture(self.infile)
        self.length = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        self.index = 0

    def __next__(self):
        """Get next image from video."""
        if self.index < self.length:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.index)
            ret, frame = self.cap.read()
            self.index += 1
            return frame
        else:
            self.cap.release()
            raise StopIteration()
