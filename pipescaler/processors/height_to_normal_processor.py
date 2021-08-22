#!/usr/bin/env python
#   pipescaler/processors/height_to_normal_processor.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
""""""
from __future__ import annotations

from argparse import ArgumentParser
from logging import info
from typing import Any, Optional, Tuple

from PIL import Image

from pipescaler.common import validate_float
from pipescaler.core import (
    Processor,
    UnsupportedImageModeError,
    crop_image,
    expand_image,
    gaussian_smooth_image,
    normal_map_from_heightmap,
    remove_palette_from_image,
)


class HeightToNormalProcessor(Processor):

    # region Builtins

    def __init__(self, sigma: Optional[int] = None, **kwargs: Any) -> None:
        """
        Validates and stores static configuration.

        Arguments:
            pixels (Tuple[int]): Number of pixels to remove from left, top, right, and
              bottom
        """
        super().__init__(**kwargs)

        # Store configuration
        if sigma is not None:
            self.sigma = validate_float(sigma, min_value=0)
        else:
            self.sigma = None

    # endregion

    # region Methods

    def process_file(self, infile: str, outfile: str) -> None:
        """
        Expands infile and writes the resulting output to outfile.

        Arguments:
            infile (str): Input file
            outfile (str): Output file
        """

        # Read image
        input_image = Image.open(infile)
        if input_image.mode == "P":
            input_image = remove_palette_from_image(input_image)
        if input_image.mode != "L":
            raise UnsupportedImageModeError(
                f"Image mode '{input_image.mode}' of image '{infile}'"
                f" is not supported by {type(self)}"
            )

        # Process image
        expanded_image = expand_image(input_image, 8, 8, 8, 8)
        if self.sigma is not None:
            smoothed_image = gaussian_smooth_image(expanded_image, self.sigma)
            normal_image = normal_map_from_heightmap(smoothed_image)
        else:
            normal_image = normal_map_from_heightmap(expanded_image)
        output_image = crop_image(normal_image, 8, 8, 8, 8)

        # Write image
        output_image.save(outfile)
        info(f"{self}: '{outfile}' saved")

    # endregion

    # region Class Methods

    @classmethod
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """
        Constructs argument parser.

        Returns:
            parser (ArgumentParser): Argument parser
        """
        description = kwargs.get("description", __doc__.strip())
        parser = super().construct_argparser(description=description, **kwargs)

        # Operations
        parser.add_argument(
            "--sigma",
            default=None,
            type=cls.float_arg(min_value=0),
            help="Gaussian smoothing to apply to image before calculating normal map"
            " (default: %(default)s)",
        )

        return parser

    # endregion


if __name__ == "__main__":
    HeightToNormalProcessor.main()