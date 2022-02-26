#!/usr/bin/env python
#   pipescaler/processors/image/xbrz_processor.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Upscales image using xbrz"""
from __future__ import annotations

from argparse import ArgumentParser
from inspect import cleandoc
from typing import Any

import numpy as np
import xbrz
from PIL import Image

from pipescaler.common import validate_int
from pipescaler.core import ImageProcessor, convert_mode


class XbrzProcessor(ImageProcessor):
    """Upscales image using [xbrz](https://github.com/ioistired/xbrz.py)"""

    def __init__(self, scale: int = 4, **kwargs: Any) -> None:
        """
        Validate and store static configuration

        Arguments:
            scale: Factor by which to scale output image relative to input
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Store configuration
        self.scale = validate_int(scale, 2, 6)

    def process(self, input_image: Image.Image) -> Image.Image:
        """
        Process an image

        Arguments:
            input_image: Input image to process
        Returns:
            Processed output image
        """
        input_image, input_mode = convert_mode(input_image, "RGBA")

        output_image = xbrz.scale_pillow(input_image, self.scale)
        if input_mode == "RGB":
            output_image = Image.fromarray(np.array(output_image)[:, :, :3])
        elif input_mode == "LA":
            output_image = output_image.convert("LA")
        elif input_mode in ("1", "L"):
            output_image = Image.fromarray(np.array(output_image)[:, :, :3]).convert(
                "L"
            )

        return output_image

    @classmethod
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """
        Construct argument parser

        Arguments:
            **kwargs: Additional keyword arguments

        Returns:
            parser: Argument parser
        """
        description = kwargs.pop(
            "description", cleandoc(cls.__doc__) if cls.__doc__ is not None else ""
        )
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
