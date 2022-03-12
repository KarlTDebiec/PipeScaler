#!/usr/bin/env python
#   pipescaler/mergers/palette_match_merger.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Matches an image's color palette to that of a reference image"""
from __future__ import annotations

from typing import Dict, List

import numpy as np
from PIL import Image
from scipy.spatial.distance import cdist
from skimage.exposure import match_histograms

from pipescaler.core import Merger


class PaletteMatchMerger(Merger):
    """Matches an image's color palette to that of a reference image"""

    @property
    def inlets(self) -> List[str]:
        """Inlets that flow into stage"""
        return ["reference", "input"]

    @property
    def supported_input_modes(self) -> Dict[str, List[str]]:
        """Supported modes for input images"""
        return {
            "reference": ["RGB"],
            "input": ["RGB"],
        }

    def merge(self, *input_images: Image.Image) -> Image.Image:
        """
        Merge images

        Arguments:
            *input_images: Input images to merge
        Returns:
            Merged output image
        """
        reference_image, input_image = input_images

        # noinspection PyTypeChecker
        input_array = np.array(input_image)
        reference_colors = np.array([a[1] for a in reference_image.getcolors(16581375)])
        input_colors = np.array([a[1] for a in input_image.getcolors(16581375)])
        dist = cdist(reference_colors, input_colors, self.weighted_distance)
        best_fit_indexes = dist.argmin(axis=0)
        output_array = np.zeros_like(input_array)
        for old_color, best_fit_index in zip(input_colors, best_fit_indexes):
            new_color = reference_colors[best_fit_index]
            output_array[np.all(input_array == old_color, axis=2)] = new_color

        output_image = Image.fromarray(output_array)
        return output_image

    @staticmethod
    def weighted_distance(color_1: np.ndarray, color_2: np.ndarray) -> float:
        rmean = (color_1[0] + color_2[0]) / 2
        dr = color_1[0] - color_2[0]
        dg = color_1[1] - color_2[1]
        db = color_1[2] - color_2[2]
        return (
            ((2 + (rmean / 256)) * (dr**2))
            + (4 * (dg**2))
            + ((2 + ((255 - rmean) / 256)) * (db**2))
        )
