#!/usr/bin/env python
#   pipescaler/processors/solid_color_processor.py
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
from typing import Any

import numpy as np
from PIL import Image

from pipescaler.core import Processor


####################################### CLASSES ########################################
class SolidColorProcessor(Processor):

    # region Methods

    def process_file(self, infile: str, outfile: str, **kwargs: Any) -> None:
        """
        Calculates average color of infile and writes new image of equivalent size and
        mode to outfile.

        Arguments:
            infile (str): Input file
            outfile (str): Output file
        """

        # Read image
        input_image = Image.open(infile)
        input_datum = np.array(input_image)

        # Convert image
        if input_image.mode in ("RGBA", "RGB", "LA"):
            color = tuple(np.rint(input_datum.mean(axis=(0, 1))).astype(np.uint8))
        elif input_image.mode == "L":
            color = round(input_datum.mean())
        else:
            raise ValueError()
        output_image = Image.new(input_image.mode, input_image.size, color)

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
            "--scale",
            default=1,
            type=cls.float_arg(min_value=0),
            help="scaling factor (default: %(default)s)",
        )

        return parser

    # endregion


######################################### MAIN #########################################
if __name__ == "__main__":
    SolidColorProcessor.main()
