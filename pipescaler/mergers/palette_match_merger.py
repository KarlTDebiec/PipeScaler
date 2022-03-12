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

from pipescaler.core import Merger, get_colors


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
        reference_array = np.array(reference_image)
        reference_colors = get_colors(reference_image)
        # noinspection PyTypeChecker
        input_array = np.array(input_image)
        input_colors = get_colors(input_image)

        dist = cdist(reference_colors, input_colors, self.weighted_distance)

        nay = False
        if nay:
            best_fit_indexes = dist.argmin(axis=0)
            output_array = np.zeros_like(input_array)
            for old_color, best_fit_index in zip(input_colors, best_fit_indexes):
                new_color = reference_colors[best_fit_index]
                output_array[np.all(input_array == old_color, axis=2)] = new_color
        else:
            reference_array_indexed = np.zeros(reference_array.shape[:-1], int)
            for i, color in enumerate(reference_colors):
                reference_array_indexed[np.all(reference_array == color, axis=2)] = i

            ok_colors = np.zeros(
                (*reference_array.shape[:-1], reference_colors.shape[0]), bool
            )
            for i in range(reference_colors.shape[0]):
                ok = reference_array_indexed == i
                ok_colors[ok, i] = True
                ok_colors[:-1, :-1, i] = ok_colors[:-1, :-1, i] | ok[1:, 1:]
                ok_colors[:, :-1, i] = ok_colors[:, :-1, i] | ok[:, 1:]
                ok_colors[1:, :-1, i] = ok_colors[1:, :-1, i] | ok[:-1, 1:]
                ok_colors[:-1, :, i] = ok_colors[:-1, :, i] | ok[1:, :]
                ok_colors[1:, :, i] = ok_colors[1:, :, i] | ok[:-1, :]
                ok_colors[:-1, 1:, i] = ok_colors[:-1, 1:, i] | ok[1:, :-1]
                ok_colors[:, 1:, i] = ok_colors[:, 1:, i] | ok[:, :-1]
                ok_colors[1:, 1:, i] = ok_colors[1:, 1:, i] | ok[:-1, :-1]

            input_array_indexed = np.zeros(input_array.shape[:-1], int)
            for i, color in enumerate(input_colors):
                input_array_indexed[np.all(input_array == color, axis=2)] = i

            output_array_indexed = np.zeros(input_array.shape[:-1], int)
            for input_x in range(input_array.shape[0]):
                for input_y in range(input_array.shape[1]):
                    reference_x = int(np.floor(input_x / 4))
                    reference_y = int(np.floor(input_y / 4))
                    input_color_index = input_array_indexed[input_x, input_y]
                    dist_here = np.copy(dist[:, input_color_index])
                    ok_colors_here = ok_colors[reference_x, reference_y]
                    dist_here[~ok_colors_here] = np.nan
                    best = np.nanargmin(dist_here)
                    output_array_indexed[input_x, input_y] = best
            output_array = np.zeros_like(input_array)
            for i, color in enumerate(reference_colors):
                output_array[output_array_indexed == i] = color

        output_image = Image.fromarray(output_array)
        return output_image

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
