#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Sorts video based on aspect ratio."""
from __future__ import annotations

from logging import info
from typing import Optional

import cv2
import numpy as np

from pipescaler.core.pipelines.video import PipeVideo, VideoSorter


class AspectRatioSorter(VideoSorter):
    """Sorts image based on canvas size."""

    def __init__(self, **outlets: dict[str, float]) -> None:
        """Initialize.

        Arguments:
            **outlets: Outlets to which videos may be sorted; keys are outlet names,
            such as 'four_three' or 'sixteen_nine'; values are aspect ratios
        """
        self._outlets = {k: str(v) for k, v in outlets.items()}

    def __call__(self, pipe_object: PipeVideo) -> Optional[str]:
        """Get the outlet to which a video should be sorted.

        Arguments:
            pipe_object: Video to sort
        Returns:
            Outlet to which image should be sorted
        """
        outlet = None
        width = pipe_object.video.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = pipe_object.video.get(cv2.CAP_PROP_FRAME_HEIGHT)
        for outlet_name, aspect_ratio in self._outlets.items():
            precision = len(aspect_ratio.split(".")[1])
            if str(np.round(width / height, precision)) == aspect_ratio:
                outlet = outlet_name
        if outlet:
            info(f"{self}: '{pipe_object.location_name}' matches '{outlet}'")
        else:
            info(f"{self}: '{pipe_object.location_name}' does not match any outlet")
        return outlet

    def __repr__(self) -> str:
        """Representation."""
        outlets_str = ", ".join(f"{k}={v}" for k, v in self._outlets.items())
        return f"{self.__class__.__name__}({outlets_str})"

    @property
    def outlets(self) -> tuple[str, ...]:
        """Outlets to which videos may be sorted."""
        return tuple(self._outlets.values())
