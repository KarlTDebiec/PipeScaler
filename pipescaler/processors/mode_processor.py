#!/usr/bin/env python
#   pipescaler/processors/mode_processor.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Converts mode of image"""
from __future__ import annotations

from argparse import ArgumentParser
from inspect import cleandoc
from logging import info
from typing import Any

from PIL import Image, ImageColor

from pipescaler.common import validate_str
from pipescaler.core import Processor, validate_image


class ModeProcessor(Processor):
    """Converts mode of image."""

    modes = ["L", "LA", "RGB", "RGBA"]

    def __init__(
        self,
        mode: str = "RGB",
        background_color: str = "#000000",
        **kwargs: Any,
    ) -> None:
        """
        Validate and store static configuration

        Arguments:
            mode: Output mode
            background_color: Background color of image
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Store configuration
        self.mode = validate_str(mode, self.modes)
        self.background_color = ImageColor.getrgb(background_color)  # TODO: Validate

    def __call__(self, infile: str, outfile: str) -> None:
        """
        Converts infile mode and writes the resulting output to outfile.

        Arguments:
            infile (str): Input file
            outfile (str): Output file
        """
        # Read image
        input_image = validate_image(infile, ["L", "LA", "RGB", "RGBA"])

        # Process image
        if input_image.mode == self.mode:
            output_image = input_image
        else:
            output_image = Image.new("RGBA", input_image.size, self.background_color)
            output_image.paste(input_image)
            if self.mode != "RGBA":
                output_image = output_image.convert(self.mode)

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
            "--mode",
            default="RGBA",
            type=cls.str_arg(options=cls.modes),
            help="image mode ('RGBA', 'RGB', 'LA', or 'L', default: %(default)s)",
        )
        parser.add_argument(
            "--background_color",
            default="#000000",
            type=str,
            help="background color of output image; only relevant if input image is "
            "RGBA or LA (default: %(default)s)",
        )

        return parser


if __name__ == "__main__":
    ModeProcessor.main()
