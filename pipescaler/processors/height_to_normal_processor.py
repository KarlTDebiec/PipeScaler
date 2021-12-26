#!/usr/bin/env python
#   pipescaler/processors/height_to_normal_processor.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Converts height map image to a normal map image"""
from __future__ import annotations

from argparse import ArgumentParser
from inspect import cleandoc
from logging import info
from typing import Any, Optional, Tuple

from pipescaler.common import validate_float
from pipescaler.core import (
    Processor,
    crop_image,
    expand_image,
    generate_normal_map_from_height_map_image,
    smooth_image,
    validate_image,
)


class HeightToNormalProcessor(Processor):
    """Converts height map image to a normal map image."""

    def __init__(self, sigma: Optional[int] = None, **kwargs: Any) -> None:
        """
        Validates and stores static configuration.
        """
        super().__init__(**kwargs)

        # Store configuration
        if sigma is not None:
            self.sigma = validate_float(sigma, min_value=0)
        else:
            self.sigma = None

    def __call__(self, infile: str, outfile: str) -> None:
        # Read image
        input_image = validate_image(infile, "L")

        # Process image
        expanded_image = expand_image(input_image, 8, 8, 8, 8)
        if self.sigma is not None:
            smoothed_image = smooth_image(expanded_image, self.sigma)
            normal_image = generate_normal_map_from_height_map_image(smoothed_image)
        else:
            normal_image = generate_normal_map_from_height_map_image(expanded_image)
        output_image = crop_image(normal_image, 8, 8, 8, 8)

        # Write image
        output_image.save(outfile)
        info(f"{self}: '{outfile}' saved")

    @classmethod
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """
        Construct argument parser

        Args:
            kwargs: Additional keyword arguments

        Returns:
            parser: Argument parser
        """
        description = kwargs.pop("description", cleandoc(cls.__doc__))
        parser = super().construct_argparser(description=description, **kwargs)

        # Operations
        parser.add_argument(
            "--sigma",
            default=None,
            type=cls.float_arg(min_value=0),
            help="Gaussian smoothing to apply to image before calculating normal map "
            "(default: %(default)s)",
        )

        return parser


if __name__ == "__main__":
    HeightToNormalProcessor.main()
