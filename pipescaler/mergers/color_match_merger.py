#!/usr/bin/env python
#   pipescaler/mergers/merger.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Matches an image's color histogram to that of a reference image"""
from __future__ import annotations

from typing import Dict, List

import numpy as np
from PIL import Image
from skimage.exposure import match_histograms

from pipescaler.core import Merger, UnsupportedImageModeError


class ColorMatchMerger(Merger):
    """Matches an image's color histogram to that of a reference image"""

    @property
    def inlets(self) -> List[str]:
        """Inlets that flow into stage"""
        return ["reference", "input"]

    @property
    def supported_input_modes(self) -> Dict[str, List[str]]:
        return {
            "reference": ["L", "LA", "RGB", "RGBA"],
            "input": ["L", "LA", "RGB", "RGBA"],
        }

    def merge(self, *input_images: Image.Image) -> Image.Image:
        """
        Match an image's color histogram to that of a reference image
        """

        # Read images
        reference_image, input_image = input_images
        if reference_image.mode != input_image.mode:
            raise UnsupportedImageModeError(
                f"Image mode '{reference_image.mode}' of reference image"
                f" does not match mode '{input_image.mode}' of input image"
            )

        # Merge images
        # noinspection PyTypeChecker
        reference_array = np.array(reference_image)
        # noinspection PyTypeChecker
        input_array = np.array(input_image)
        if reference_image.mode == "L":
            output_array = match_histograms(input_array, reference_array)
        else:
            output_array = match_histograms(
                input_array, reference_array, channel_axis=0
            )
        output_array = np.clip(output_array, 0, 255).astype(np.uint8)
        output_image = Image.fromarray(output_array)

        return output_image
