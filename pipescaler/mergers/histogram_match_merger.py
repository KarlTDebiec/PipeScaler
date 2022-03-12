#!/usr/bin/env python
#   pipescaler/mergers/color_match_merger.py
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


class HistogramMatchMerger(Merger):
    """Matches an image's color histogram to that of a reference image"""

    @property
    def inlets(self) -> List[str]:
        """Inlets that flow into stage"""
        return ["reference", "fit"]

    @property
    def supported_input_modes(self) -> Dict[str, List[str]]:
        """Supported modes for input images"""
        return {
            "reference": ["L", "LA", "RGB", "RGBA"],
            "fit": ["L", "LA", "RGB", "RGBA"],
        }

    def merge(self, *input_images: Image.Image) -> Image.Image:
        """
        Merge images

        Arguments:
            *input_images: Input images to merge
        Returns:
            Merged output image
        """
        ref_image, fit_image = input_images
        if ref_image.mode != fit_image.mode:
            raise UnsupportedImageModeError(
                f"Image mode '{ref_image.mode}' of reference image"
                f" does not match mode '{fit_image.mode}' of fit image"
            )

        # noinspection PyTypeChecker
        ref_array = np.array(ref_image)
        # noinspection PyTypeChecker
        fit_array = np.array(fit_image)
        if ref_image.mode == "L":
            output_array = match_histograms(fit_array, ref_array)
        else:
            output_array = match_histograms(fit_array, ref_array, channel_axis=0)
        output_array = np.clip(output_array, 0, 255).astype(np.uint8)
        output_image = Image.fromarray(output_array)

        return output_image