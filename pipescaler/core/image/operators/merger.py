#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Combines two or more images into a single downstream image."""
from __future__ import annotations

from abc import ABC, abstractmethod

from PIL import Image

from pipescaler.core.image.operator import Operator


class Merger(Operator, ABC):
    """Merges two or more images into a single downstream image."""

    @abstractmethod
    def __call__(self, *input_images: Image.Image) -> Image.Image:
        """Merge images.

        Arguments:
            input_images: Input images
        Returns:
            Merged output image
        """
        raise NotImplementedError()
