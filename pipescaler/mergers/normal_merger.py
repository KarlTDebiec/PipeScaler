#!/usr/bin/env python
#   pipescaler/mergers/merger.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Merges x, y, and z images into a single normal map image"""
from __future__ import annotations

from typing import Dict, List

import numpy as np
from PIL import Image

from pipescaler.core import Merger


class NormalMerger(Merger):
    """Merges x, y, and z images into a single normal map image"""

    @property
    def inlets(self) -> List[str]:
        """Inlets that flow into stage"""
        return ["x", "y", "z"]

    @property
    def supported_input_modes(self) -> Dict[str, List[str]]:
        return {
            "x": ["L"],
            "y": ["L"],
            "z": ["L"],
        }

    def merge(self, *input_images: Image.Image) -> Image.Image:
        """
        Merge x, y, and z images into a single normal map image
        """
        x_image, y_image, z_image = input_images

        # Merge images
        # noinspection PyTypeChecker
        x_array = np.clip(np.array(x_image, float) - 128, -128, 127)
        # noinspection PyTypeChecker
        y_array = np.clip(np.array(y_image, float) - 128, -128, 127)
        # noinspection PyTypeChecker
        z_array = np.clip(np.array(z_image, float) / 2, 0, 127)
        magnitude = np.sqrt(x_array**2 + y_array**2 + z_array**2)
        x_array = np.clip(((x_array / magnitude) * 128) + 128, 0, 255).astype(np.uint8)
        y_array = np.clip(((y_array / magnitude) * 128) + 128, 0, 255).astype(np.uint8)
        z_array = np.clip(((z_array / magnitude) * 128) + 128, 0, 255).astype(np.uint8)
        output_array = np.zeros((*x_array.shape, 3), np.uint8)
        output_array[:, :, 0] = x_array
        output_array[:, :, 1] = y_array
        output_array[:, :, 2] = z_array
        output_image = Image.fromarray(output_array)

        return output_image
