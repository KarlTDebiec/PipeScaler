#!/usr/bin/env python
#   pipescaler/processors/image/sharpen_processor.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Sharpens an image"""
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


class SharpenProcessor(ImageProcessor):
    """Sharpens an image"""

    @property
    def supported_input_modes(self) -> List[str]:
        return ["L", "RGB"]

    def process(self, input_image: Image.Image) -> Image.Image:
        """
        Read image from infile, process it, and save to outfile

        Arguments:
            infile: Input file path
            outfile: Output file path
        """
        expanded_image = expand_image(input_image, 8, 8, 8, 8)

        output_image = crop_image(expanded_image, 8, 8, 8, 8)

        return output_image


if __name__ == "__main__":
    SharpenProcessor.main()
