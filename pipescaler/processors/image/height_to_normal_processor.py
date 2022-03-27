#!/usr/bin/env python
#   pipescaler/processors/image/height_to_normal_processor.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Converts height map image to a normal map image."""
from __future__ import annotations

from argparse import ArgumentParser
from inspect import cleandoc
from typing import Any, List, Optional

from PIL import Image

from pipescaler.common import validate_float
from pipescaler.core import (
    ImageProcessor,
    crop_image,
    expand_image,
    generate_normal_map_from_height_map_image,
    smooth_image,
)


class HeightToNormalProcessor(ImageProcessor):
    """Converts height map image to a normal map image."""

    def __init__(self, sigma: Optional[int] = None, **kwargs: Any) -> None:
        """
        Validate and store static configuration

        Arguments:
            sigma: Gaussian smoothing to apply to image
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Store configuration
        if sigma is not None:
            self.sigma = validate_float(sigma, min_value=0)
        else:
            self.sigma = None

    def process(self, input_image: Image.Image) -> Image.Image:
        """
        Read image from infile, process it, and save to outfile

        Arguments:
            infile: Input file path
            outfile: Output file path
        """
        expanded_image = expand_image(input_image, 8, 8, 8, 8)
        if self.sigma is not None:
            smoothed_image = smooth_image(expanded_image, self.sigma)
            normal_image = generate_normal_map_from_height_map_image(smoothed_image)
        else:
            normal_image = generate_normal_map_from_height_map_image(expanded_image)
        output_image = crop_image(normal_image, 8, 8, 8, 8)

        return output_image

    @classmethod
    @property
    def supported_input_modes(self) -> List[str]:
        return ["L"]
