#!/usr/bin/env python
#   pipescaler/processors/crop_processor.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
from __future__ import annotations

from argparse import ArgumentParser
from inspect import cleandoc
from logging import info
from typing import Any, Tuple

from PIL import Image

from pipescaler.common import validate_ints
from pipescaler.core import Processor, crop_image


class CropProcessor(Processor):
    """Crops image canvas."""

    def __init__(self, pixels: Tuple[int], **kwargs: Any) -> None:
        """
        Validates and stores static configuration.

        Arguments:
            pixels (Tuple[int]): Number of pixels to remove from left, top, right, and
              bottom
        """
        super().__init__(**kwargs)

        # Store configuration
        self.left, self.top, self.right, self.bottom = validate_ints(
            pixels, length=4, min_value=0
        )

    def __call__(self, infile: str, outfile: str) -> None:
        """
        Crops infile and writes the resulting output to outfile.

        Arguments:
            infile (str): Input file
            outfile (str): Output file
        """

        # Read image
        input_image = Image.open(infile)
        if (
            input_image.size[0] < self.left + self.right + 1
            or input_image.size[1] < self.top + self.bottom + 1
        ):
            raise ValueError()

        # Process image
        output_image = crop_image(
            input_image, self.left, self.top, self.right, self.bottom
        )

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
            "--pixels",
            default=(8, 8, 8, 8),
            metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"),
            nargs=4,
            type=cls.int_arg(0),
            help="number of pixels to remove from left, top, right, and bottom "
            "(default: %(default)s)",
        )

        return parser


if __name__ == "__main__":
    CropProcessor.main()
