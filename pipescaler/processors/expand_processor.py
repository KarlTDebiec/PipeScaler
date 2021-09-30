#!/usr/bin/env python
#   pipescaler/processors/expand_processor.py
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
from pipescaler.core import Processor, expand_image


class ExpandProcessor(Processor):
    """Expands image canvas."""

    def __init__(self, pixels: Tuple[int], **kwargs: Any) -> None:
        """
        Validates and stores static configuration.

        Arguments:
            pixels (Tuple[int]): Number of pixels to add to left, top, right, and bottom
        """
        super().__init__(**kwargs)

        # Store configuration
        self.left, self.top, self.right, self.bottom = validate_ints(
            pixels, length=4, min_value=0
        )

    def process_file(self, infile: str, outfile: str) -> None:
        """
        Expands infile and writes the resulting output to outfile.

        Arguments:
            infile (str): Input file
            outfile (str): Output file
        """

        # Read image
        input_image = Image.open(infile)

        # Expand image
        output_image = expand_image(
            input_image, self.left, self.top, self.right, self.bottom
        )

        # Write image
        output_image.save(outfile)
        info(f"{self}: '{outfile}' saved")

    @classmethod
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """
        Constructs argument parser.

        Args:
            kwargs (Any): Additional keyword arguments

        Returns:
            parser (ArgumentParser): Argument parser
        """
        description = kwargs.get("description", cleandoc(cls.__doc__))
        parser = super().construct_argparser(description=description, **kwargs)

        # Operations
        parser.add_argument(
            "--pixels",
            default=(0, 0, 0, 0),
            metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"),
            nargs=4,
            type=cls.int_arg(0),
            help="number of pixels to add to left, top, right, and bottom "
            "(default: %(default)s)",
        )

        return parser


if __name__ == "__main__":
    ExpandProcessor.main()
