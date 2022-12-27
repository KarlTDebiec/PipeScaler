#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Copies videos to an output directory."""
from __future__ import annotations

from pipescaler.core.pipelines import CopyTerminus
from pipescaler.core.pipelines.video import PipeVideo, VideoTerminus


class CopyVideoTerminus(CopyTerminus, VideoTerminus):
    """Copies videos to an output directory."""

    def __call__(self, input_video: PipeVideo) -> None:
        """Save video to output directory.

        Arguments:
            input_video: Video to save to output directory
        """
        breakpoint()
        raise NotImplementedError()
