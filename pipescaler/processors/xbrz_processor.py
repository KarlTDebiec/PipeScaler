#!/usr/bin/env python
#   pipescaler/processors/xbrz_processor.py
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
from typing import Any

import numpy as np
import xbrz
from PIL import Image

from pipescaler.common import validate_int
from pipescaler.core import (
    Processor,
    UnsupportedImageModeError,
    remove_palette_from_image,
)


class XbrzProcessor(Processor):
    def __init__(self, scale: int = 4, **kwargs: Any) -> None:
        """
        Validates and stores static configuration.

        Arguments:
            scale (int): Factor by which to scale images
        """
        super().__init__(**kwargs)

        # Store configuration
        self.scale = validate_int(scale, 2, 6)

    def __call__(self, infile: str, outfile: str) -> None:
        """
        Scales infile by self.scale and writes the resulting image to outfile.

        Arguments:
            infile (str): Input file
            outfile (str): Output file
        """
        self.process_file(infile, outfile)

    def process_file(self, infile: str, outfile: str) -> None:
        """
        Scales infile and writes the resulting output to outfile.

        Arguments:
            infile (str): Input file
            outfile (str): Output file
        """

        # Read image
        input_image = Image.open(infile)
        if input_image.mode == "P":
            input_image = remove_palette_from_image(input_image)
        if input_image.mode == "RGBA":
            rgba_image = input_image
        elif input_image.mode in ("RGB", "LA", "L"):
            rgba_image = input_image.convert("RGBA")
        else:
            raise UnsupportedImageModeError(
                f"Image mode '{input_image.mode}' of image '{infile}'"
                f" is not supported by {type(self)}"
            )

        # Process image
        output_image = xbrz.scale_pillow(rgba_image, self.scale)
        if input_image.mode == "RGB":
            output_image = Image.fromarray(np.array(output_image)[:, :, :3])
        elif input_image.mode == "LA":
            output_image = output_image.convert("LA")
        elif input_image.mode == "L":
            output_image = Image.fromarray(np.array(output_image)[:, :, :3])
            output_image = output_image.convert("L")

        # Write image
        output_image.save(outfile)
        info(f"{self}: '{outfile}' saved")

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


if __name__ == "__main__":
    XbrzProcessor.main()
