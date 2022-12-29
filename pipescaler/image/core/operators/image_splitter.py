#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Splits one image into two or more images."""
from __future__ import annotations

from abc import ABC, abstractmethod

from PIL import Image

from pipescaler.image.core.image_operator import ImageOperator


class ImageSplitter(ImageOperator, ABC):
    """Splits one image into two or more images."""

    @abstractmethod
    def __call__(self, input_image: Image.Image) -> tuple[Image.Image, ...]:
        """Split an image.

        Arguments:
            input_image: Input image
        Returns:
            Split output images
        """
        raise NotImplementedError()
