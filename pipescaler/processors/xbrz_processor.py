#!/usr/bin/env python
#   pipescaler/processors/xbrz_processor.py
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
import xbrz
from PIL import Image

from pipescaler.common import validate_int
from pipescaler.core import Processor


####################################### CLASSES ########################################
class XbrzProcessor(Processor):

    # region Builtins

    def __init__(self, scale: int = 4, **kwargs: Any) -> None:
        """
        Validates and stores static configuration.

        Arguments:
            scale (int): Factor by which to scale images
        """
        super().__init__(**kwargs)

        # Store configuration
        self.scale = validate_int(scale, 2, 6)

    # endregion

    # region Methods

    def __call__(self, infile: str, outfile: str) -> None:
        """
        Scales infile by self.scale and writes the resulting image to outfile.

        Arguments:
            infile (str): Input file
            outfile (str): Output file
        """
        self.process_file(infile, outfile, scale=self.scale)

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

        # Input
        parser.add_argument(
            "--scale",
            default=2,
            type=cls.int_arg(min_value=2, max_value=6),
            help="factor by which to scale image (2-6, default: %(default)s)",
        )

        return parser

    @classmethod
    def process_file(cls, infile: str, outfile: str, **kwargs: Any) -> None:
        """
        Scales infile by scale and writes the resulting image to outfile.

        Arguments:
            infile (str): Input file
            outfile (str): Output file
            scale (int): Factor by which to scale image
        """
        scale = validate_int(kwargs.get("scale", 2), 2, 6)

        # Read image
        input_image = Image.open(infile)
        mode = input_image.mode

        # Process image
        if mode in ("RGB", "L"):
            input_image = input_image.convert("RGBA")
        output_image = xbrz.scale_pillow(input_image, scale)
        if mode in ("RGB", "L"):
            output_image = Image.fromarray(np.array(output_image)[:, :, :3])
        if mode == "L":
            output_image = output_image.convert("L")

        # Write image
        output_image.save(outfile)
        info(f"{cls}: '{outfile}' saved")

    # endregion


######################################### MAIN #########################################
if __name__ == "__main__":
    XbrzProcessor.main()
