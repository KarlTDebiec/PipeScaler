#!/usr/bin/env python
#   pipescaler/splitter/splitter.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Splits a normal map image into separate x, y, and z images"""
from __future__ import annotations

from typing import List, Tuple

import numpy as np
from PIL import Image

from pipescaler.core import Splitter


class NormalSplitter(Splitter):
    """Splits a normal map image into separate x, y, and z images"""

    @property
    def outlets(self) -> List[str]:
        """Outlets that flow out of stage"""
        return ["x", "y", "z"]

    @property
    def supported_input_modes(self) -> List[str]:
        """Supported modes for input image"""
        return ["RGB"]

    def split(self, input_image: Image.Image) -> Tuple[Image.Image, ...]:
        """
        Split an image

        Arguments:
            input_image: Input image to split
        Returns:
            Split output images
        """
        # noinspection PyTypeChecker
        input_array = np.array(input_image)
        x_array = input_array[:, :, 0]
        y_array = input_array[:, :, 1]
        z_array = (input_array[:, :, 2].astype(float) - 128) * 2
        z_array = np.clip(z_array, 0, 255).astype(np.uint8)

        x_image = Image.fromarray(x_array)
        y_image = Image.fromarray(y_array)
        z_image = Image.fromarray(z_array)

        return x_image, y_image, z_image
