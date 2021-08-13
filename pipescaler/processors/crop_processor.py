#!/usr/bin/env python
#   pipescaler/processors/crop_processor.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
""""""
####################################### MODULES ########################################
from __future__ import annotations

from argparse import ArgumentParser
from logging import info
from typing import Any, Tuple

from PIL import Image

from pipescaler.common import validate_ints
from pipescaler.core import Processor, crop_image


####################################### CLASSES ########################################
class CropProcessor(Processor):

    # region Builtins

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

    # endregion

    # region Methods

    def process_file(self, infile: str, outfile: str) -> None:
        """
        Crops infile and writes the resulting output to outfile.

        Arguments:
            infile (str): Input file
            outfile (str): Output file
        """

        # Read image
        image = Image.open(infile)

        # Expand image
        cropped = crop_image(image, self.left, self.top, self.right, self.bottom)
        # TODO: Validate that size is viable

        # Write image
        cropped.save(outfile)
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
            "--pixels",
            default=(8, 8, 8, 8),
            metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"),
            nargs=4,
            type=cls.int_arg(0),
            help="number of pixels to remove from left, top, right, and bottom "
            "(default: %(default)s)",
        )

        return parser

    # endregion


######################################### MAIN #########################################
if __name__ == "__main__":
    CropProcessor.main()
