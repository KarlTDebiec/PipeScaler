#!/usr/bin/env python
#   pipescaler/processors/solid_color_processor.py
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
from PIL import Image

from pipescaler.common import validate_float
from pipescaler.core import (
    Processor,
    UnsupportedImageModeError,
    remove_palette_from_image,
)


class SolidColorProcessor(Processor):
    def __init__(self, scale: float = 1, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        # Store configuration
        self.scale = validate_float(scale)

    def process_file(self, infile: str, outfile: str, **kwargs: Any) -> None:
        """
        Calculates average color of infile and writes new image of equivalent
        size and mode to outfile.

        Arguments:
            infile (str): Input file
            outfile (str): Output file
        """

        # Read image
        input_image = Image.open(infile)
        if input_image.mode == "P":
            input_image = remove_palette_from_image(input_image)
        input_datum = np.array(input_image)

        # Convert image
        if input_image.mode in ("RGBA", "RGB", "LA"):
            color = tuple(np.rint(input_datum.mean(axis=(0, 1))).astype(np.uint8))
        elif input_image.mode == "L":
            color = round(input_datum.mean())
        else:
            raise UnsupportedImageModeError(
                f"Image mode '{input_image.mode}' of image '{infile}'"
                f" is not supported by {type(self)}"
            )
        output_image = Image.new(
            input_image.mode,
            (
                int(round(input_image.size[0] * self.scale)),
                int(round(input_image.size[1] * self.scale)),
            ),
            color,
        )

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
