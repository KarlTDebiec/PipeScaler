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

from enum import Enum, auto
from typing import Any, Dict, List, Union

import numpy as np
from PIL import Image
from scipy.spatial.distance import cdist

from pipescaler.common import validate_enum, validate_int
from pipescaler.core import Merger, get_colors


class PaletteMatchMode(Enum):
    """Mode of matching to perform"""

    BASIC = auto()
    LOCAL = auto()


class PaletteMatchMerger(Merger):
    """Matches an image's color palette to that of a reference image"""

    def __init__(
        self,
        palette_match_mode: Union[PaletteMatchMode, str] = PaletteMatchMode.BASIC,
        **kwargs: Any,
    ) -> None:
        """
        Validate and store static configuration

        Arguments:
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        self.palette_match_mode = validate_enum(palette_match_mode, PaletteMatchMode)

    @property
    def inlets(self) -> List[str]:
        """Inlets that flow into stage"""
        return ["reference", "fit"]

    @property
    def supported_input_modes(self) -> Dict[str, List[str]]:
        """Supported modes for input images"""
        return {
            "reference": ["RGB"],
            "fit": ["RGB"],
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

        # Get colors in reference
        # noinspection PyTypeChecker
        ref_array = np.array(ref_image)
        ref_colors = get_colors(ref_image)
        ref_array_by_index = np.zeros(ref_array.shape[:-1], int)
        for i, color in enumerate(ref_colors):
            ref_array_by_index[np.all(ref_array == color, axis=2)] = i

        # Get colors in fit
        # noinspection PyTypeChecker
        fit_array = np.array(fit_image)
        fit_colors = get_colors(fit_image)
        fit_array_by_index = np.zeros(fit_array.shape[:-1], int)
        for i, color in enumerate(fit_colors):
            fit_array_by_index[np.all(fit_array == color, axis=2)] = i

        # Calculate weighted distance between all reference and fit colors
        dist = cdist(ref_colors, fit_colors, self.weighted_distance)

        if self.palette_match_mode == PaletteMatchMode.BASIC:
            # Replace each fit pixel's color with the closest reference color
            output_array = np.zeros_like(fit_array)
            for fit_index, ref_index in enumerate(dist.argmin(axis=0)):
                output_array[fit_array_by_index == fit_index] = ref_colors[ref_index]
        elif self.palette_match_mode == PaletteMatchMode.LOCAL:
            # Replace each fit pixel's color with the closest reference color observed
            # in a 3x3 window around the fit pixel's corresponding reference pixel
            scale = validate_int(fit_array.shape[0] / ref_array.shape[0])
            local_colors = self.get_local_colors(ref_array_by_index)

            output_array_by_index = np.zeros_like(fit_array_by_index)
            for fit_x in range(fit_array.shape[0]):
                for fit_y in range(fit_array.shape[1]):
                    ref_x = int(np.floor(fit_x / scale))
                    ref_y = int(np.floor(fit_y / scale))

                    dist_xy = np.copy(dist[:, fit_array_by_index[fit_x, fit_y]])
                    dist_xy[~local_colors[ref_x, ref_y]] = np.nan
                    best = np.nanargmin(dist_xy)
                    output_array_by_index[fit_x, fit_y] = best

            output_array = np.zeros_like(fit_array)
            for i, color in enumerate(ref_colors):
                output_array[output_array_by_index == i] = color
        else:
            raise ValueError()

        output_image = Image.fromarray(output_array)
        return output_image

    @staticmethod
    def get_local_colors(array_by_index):
        local_colors = np.zeros((*array_by_index.shape, array_by_index.max() + 1), bool)
        for i in range(array_by_index.max() + 1):
            equal_i = array_by_index == i
            local_colors[equal_i, i] = True
            local_colors[:-1, :-1, i] = local_colors[:-1, :-1, i] | equal_i[1:, 1:]
            local_colors[:, :-1, i] = local_colors[:, :-1, i] | equal_i[:, 1:]
            local_colors[1:, :-1, i] = local_colors[1:, :-1, i] | equal_i[:-1, 1:]
            local_colors[:-1, :, i] = local_colors[:-1, :, i] | equal_i[1:, :]
            local_colors[1:, :, i] = local_colors[1:, :, i] | equal_i[:-1, :]
            local_colors[:-1, 1:, i] = local_colors[:-1, 1:, i] | equal_i[1:, :-1]
            local_colors[:, 1:, i] = local_colors[:, 1:, i] | equal_i[:, :-1]
            local_colors[1:, 1:, i] = local_colors[1:, 1:, i] | equal_i[:-1, :-1]

        return local_colors

    @staticmethod
    def weighted_distance(color_1: np.ndarray, color_2: np.ndarray) -> float:
        """
        Calculate the squared distance between two colors, adjusted for perception

        Args:
            color_1: Color 1
            color_2: Color 2
        Returns:
            Squared distance between two colors
        """
        rmean = (color_1[0] + color_2[0]) / 2
        dr = color_1[0] - color_2[0]
        dg = color_1[1] - color_2[1]
        db = color_1[2] - color_2[2]
        return (
            ((2 + (rmean / 256)) * (dr**2))
            + (4 * (dg**2))
            + ((2 + ((255 - rmean) / 256)) * (db**2))
        )
