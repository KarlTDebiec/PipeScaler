#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Sorts video based on aspect ratio."""
from __future__ import annotations

import cv2
import numpy as np

from pipescaler.core.pipelines import PipeVideo
from pipescaler.core.pipelines.sorter import Sorter


class AspectRatioSorter(Sorter):
    """Sorts image based on canvas size."""

    def __init__(self, **outlets: dict[str, float]) -> None:
        """Initialize.

        Arguments:
            **outlets: Outlets to which videos may be sorted; keys are outlet names;
            values are aspect ratios
        """
        self._outlets = {k: str(v) for k, v in outlets.items()}

    def __call__(self, pipe_object: PipeVideo) -> str:
        """Get the outlet to which a video should be sorted.

        Arguments:
            pipe_object: Video to sort
        Returns:
            Outlet to which image should be sorted
        """
        width = pipe_object.video.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = pipe_object.video.get(cv2.CAP_PROP_FRAME_HEIGHT)
        for outlet, aspect_ratio in self._outlets.items():
            if (
                str(np.round(width / height, len(aspect_ratio.split(".")[1])))
                == aspect_ratio
            ):
                return outlet
        return None

    def __repr__(self) -> str:
        """Representation."""
        return f"{self.__class__.__name__}(cutoff={self.cutoff!r})"

    @property
    def outlets(self) -> tuple[str, ...]:
        """Outlets to which videos may be sorted."""
        return self._outlets
