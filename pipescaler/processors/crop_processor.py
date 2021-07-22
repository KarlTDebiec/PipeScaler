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
from typing import Any, Optional, Tuple

from PIL import Image

from pipescaler.common import validate_int, validate_ints
from pipescaler.core import Processor, crop_image, expand_image


####################################### CLASSES ########################################
class CropProcessor(Processor):

    # region Builtins

    def __init__(self, crop: Optional[Tuple[int]] = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        # Store configuration
        if crop is None:
            crop = (0, 0, 0, 0)
        self.crop = validate_ints(crop, length=4, min_value=0)

    # endregion

    # region Methods

    def __call__(self, infile: str, outfile: str) -> None:
        self.process_file(infile, outfile, crop=self.crop)

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
        parser.crop(
            "--crop",
            default=(0, 0, 0, 0),
            nargs=4,
            type=cls.ints_arg(length=4, min_value=0),
            help="number of pixels to remove from left, top, right, and bottom "
            "(default: %(default)d)",
        )

        return parser

    @classmethod
    def process_file(cls, infile: str, outfile: str, **kwargs: Any) -> None:
        crop = validate_ints(kwargs.get("crop", (0, 0, 0, 0)), length=4, min_value=0)

        # Read image
        image = Image.open(infile)

        # Expand image
        cropped = crop_image(image, crop[0], crop[1], crop[2], crop[3])

        # write image
        cropped.save(outfile)
        info(f"{cls}: '{outfile}' saved")

    # endregion


######################################### MAIN #########################################
if __name__ == "__main__":
    CropProcessor.main()
