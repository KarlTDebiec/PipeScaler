#!/usr/bin/env python
#   pipescaler/processors/solid_color_processor.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Sets entire image color to its average color, optionally resizing"""
from __future__ import annotations

from argparse import ArgumentParser
from inspect import cleandoc
from logging import info
from typing import Any

import numpy as np
from PIL import Image

from pipescaler.common import validate_float
from pipescaler.core import Processor, validate_image


class SolidColorProcessor(Processor):
    """Sets entire image color to its average color, optionally resizing."""

    def __init__(self, scale: float = 1, **kwargs: Any) -> None:
        """
        Validate and store static configuration

        Args:
            scale: Factor by which to scale output image relative to input
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Store configuration
        self.scale = validate_float(scale)

    def __call__(self, infile: str, outfile: str) -> None:
        """
        Read image from infile, process it, and save to outfile

        Arguments:
            infile: Input file path
            outfile: Output file path
        """
        # Read image
        input_image = validate_image(infile, ["L", "LA", "RGB", "RGBA"])
        input_datum = np.array(input_image)

        # Process image
        size = (
            round(input_image.size[0] * self.scale),
            round(input_image.size[1] * self.scale),
        )
        if input_image.mode in ("RGBA", "RGB", "LA"):
            color = tuple(np.rint(input_datum.mean(axis=(0, 1))).astype(np.uint8))
        else:
            color = round(input_datum.mean())
        output_image = Image.new(input_image.mode, size, color)

        # Write image
        output_image.save(outfile)
        info(f"{self}: '{outfile}' saved")

    @classmethod
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """
        Construct argument parser

        Args:
            **kwargs: Additional keyword arguments

        Returns:
            parser: Argument parser
        """
        description = kwargs.pop("description", cleandoc(cls.__doc__))
        parser = super().construct_argparser(description=description, **kwargs)

        # Operations
        parser.add_argument(
            "--scale",
            default=1,
            type=cls.float_arg(min_value=0),
            help="scaling factor (default: %(default)s)",
        )

        return parser


if __name__ == "__main__":
    SolidColorProcessor.main()
