#!/usr/bin/env python
#   pipescaler/splitter/repeat_splitter.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Repeats an input image"""
from __future__ import annotations

from typing import List, Tuple

from PIL import Image

from pipescaler.core import Splitter


class RepeatSplitter(Splitter):
    """Repeats an input image"""

    @property
    def outlets(self) -> List[str]:
        """Outlets that flow out of stage"""
        return ["one", "two"]

    def split(self, input_image: Image.Image) -> Tuple[Image.Image, ...]:
        """
        Split an image

        Arguments:
            input_image: Input image to split
        Returns:
            Split output images
        """
        return input_image.copy(), input_image.copy()
