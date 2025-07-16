#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Processes an image, yielding a modified image."""

from __future__ import annotations

from abc import ABC, abstractmethod

from PIL import Image

from pipescaler.image.core.image_operator import ImageOperator


class ImageProcessor(ImageOperator, ABC):
    """Processes an image, yielding a modified image."""

    @abstractmethod
    def __call__(self, input_image: Image.Image) -> Image.Image:
        """Process an image.

        Arguments:
            input_image: Input image
        Returns:
            Processed output image
        """
        raise NotImplementedError()
