#!/usr/bin/env python
#   pipescaler/processors/resize_processor.py
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
from PIL import Image

from pipescaler.common import validate_float, validate_str
from pipescaler.core import (
    Processor,
    UnsupportedImageModeError,
    remove_palette_from_image,
)


class ResizeProcessor(Processor):
    """Resizes canvas."""

    resample_methods = {
        "bicubic": Image.BICUBIC,
        "bilinear": Image.BILINEAR,
        "lanczos": Image.LANCZOS,
        "nearest": Image.NEAREST,
    }

    def __init__(self, scale: float, resample: str = "lanczos", **kwargs: Any) -> None:
        """
        Validates and stores static configuration.

        Arguments:
            scale (float): Output image scale relative to input image
            resample (str): Resample algorithm
        """
        super().__init__(**kwargs)

        # Store configuration
        self.scale = validate_float(scale, min_value=0)
        self.resample = self.resample_methods[
            validate_str(resample, options=self.resample_methods.keys())
        ]

    def process_file(self, infile: str, outfile: str) -> None:
        """
        Rescales infile and writes the resulting output to outfile.

        Arguments:
            infile (str): Input file
            outfile (str): Output file
        """

        # Read image
        input_image = Image.open(infile)
        if input_image.mode == "P":
            input_image = remove_palette_from_image(input_image)
        input_datum = np.array(input_image)

        # Scale image
        size = (
            round(input_image.size[0] * self.scale),
            round(input_image.size[1] * self.scale),
        )
        if input_image.mode == "RGBA":
            rgba_datum = np.zeros((size[1], size[0], 4), np.uint8)
            rgba_datum[:, :, :3] = np.array(
                Image.fromarray(input_datum[:, :, :3]).resize(
                    size, resample=self.resample
                )
            )
            rgba_datum[:, :, 3] = np.array(
                Image.fromarray(input_datum[:, :, 3]).resize(
                    size, resample=self.resample
                )
            )
            output_image = Image.fromarray(rgba_datum)
        elif input_image.mode == "RGB":
            output_image = input_image.resize(size, resample=self.resample)
        elif input_image.mode == "LA":
            la_datum = np.zeros((size[1], size[0], 2), np.uint8)
            la_datum[:, :, 0] = np.array(
                Image.fromarray(input_datum[:, :, 0]).resize(
                    size, resample=self.resample
                )
            )
            la_datum[:, :, 1] = np.array(
                Image.fromarray(input_datum[:, :, 1]).resize(
                    size, resample=self.resample
                )
            )
            output_image = Image.fromarray(la_datum)
        elif input_image.mode == "L":
            output_image = input_image.resize(size, resample=self.resample)
        else:
            raise UnsupportedImageModeError(
                f"Image mode '{input_image.mode}' of image '{infile}'"
                f" is not supported by {type(self)}"
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
        description = kwargs.get("description", cleandoc(cls.__doc__))
        parser = super().construct_argparser(description=description, **kwargs)

        # Operations
        parser.add_argument(
            "--scale",
            default=2,
            type=cls.float_arg(min_value=0),
            help="scaling factor (default: %(default)s)",
        )
        parser.add_argument(
            "--resample",
            default="lanczos",
            type=cls.str_arg(options=cls.resample_methods.keys()),
            help="background color (default: %(default)s)",
        )

        return parser


if __name__ == "__main__":
    ResizeProcessor.main()
