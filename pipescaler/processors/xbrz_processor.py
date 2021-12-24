#!/usr/bin/env python
#   pipescaler/processors/xbrz_processor.py
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
from typing import Any

import numpy as np
import xbrz
from PIL import Image

from pipescaler.common import validate_int
from pipescaler.core import Processor, validate_image_and_convert_mode


class XbrzProcessor(Processor):
    """Upscales image using [xbrz](https://github.com/ioistired/xbrz.py)."""

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
        Scales infile and writes the resulting output to outfile.

        Arguments:
            infile (str): Input file
            outfile (str): Output file
        """

        # Read image
        input_image, input_mode = validate_image_and_convert_mode(
            infile, ["L", "LA", "RGB", "RGBA"], "RGBA"
        )

        # Process image
        output_image = xbrz.scale_pillow(input_image, self.scale)
        if input_mode == "RGB":
            output_image = Image.fromarray(np.array(output_image)[:, :, :3])
        elif input_mode == "LA":
            output_image = output_image.convert("LA")
        elif input_mode == "L":
            output_image = Image.fromarray(np.array(output_image)[:, :, :3])
            output_image = output_image.convert("L")

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
        description = kwargs.pop("description", cleandoc(cls.__doc__))
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
