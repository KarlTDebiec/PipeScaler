#!/usr/bin/env python
#   pipescaler/mergers/merger.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Merges alpha and color images into a single image with transparency"""
from __future__ import annotations

from logging import info
from typing import Any, Dict, List, Tuple

import numpy as np
from PIL import Image

from pipescaler.core import Merger, validate_image


class AlphaMerger(Merger):
    """Merges alpha and color images into a single image with transparency"""

    @property
    def inlets(self) -> List[str]:
        """Inlets that flow into stage"""
        return ["color", "alpha"]

    @property
    def supported_input_modes(self) -> Dict[str, List[str]]:
        return {
            "color": ["L", "RGB"],
            "alpha": ["1", "L"],
        }

    def merge(self, *input_images: Image.Image) -> Image.Image:
        """
        Merge color and alpha images into a single image with transparency
        """
        color_image, alpha_image = input_images

        # noinspection PyTypeChecker
        color_array = np.array(color_image)
        if alpha_image.mode == "L":
            # noinspection PyTypeChecker
            alpha_array = np.array(alpha_image)
        else:
            # noinspection PyTypeChecker
            alpha_array = np.array(alpha_image.convert("L"))
        if color_image.mode == "L":
            output_array = np.zeros((*color_array.shape, 2), np.uint8)
            output_array[:, :, 0] = color_array
        else:
            output_array = np.zeros((*color_array.shape[:-1], 4), np.uint8)
            output_array[:, :, :-1] = color_array
        output_array[:, :, -1] = alpha_array
        output_image = Image.fromarray(output_array)

        return output_image
