#!/usr/bin/env python
#   pipescaler/processors/image/crop_processor.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Crops image canvas"""
from __future__ import annotations

from argparse import ArgumentParser
from inspect import cleandoc
from typing import Any, Tuple

from PIL import Image

from pipescaler.common import validate_ints
from pipescaler.core import ImageProcessor, crop_image


class CropProcessor(ImageProcessor):
    """Crops image canvas"""

    name = "crop"

    def __init__(self, pixels: Tuple[int], **kwargs: Any) -> None:
        """
        Validate and store static configuration

        Arguments:
            pixels: Number of pixels to remove from left, top, right, and bottom
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Store configuration
        self.left, self.top, self.right, self.bottom = validate_ints(
            pixels, length=4, min_value=0
        )

    def process(self, input_image: Image.Image) -> Image.Image:
        """
        Process an image

        Arguments:
            input_image: Input image to process
        Returns:
            Processed output image
        """
        if (
            input_image.size[0] < self.left + self.right + 1
            or input_image.size[1] < self.top + self.bottom + 1
        ):
            raise ValueError()

        output_image = crop_image(
            input_image, self.left, self.top, self.right, self.bottom
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
        name = kwargs.pop(
            "name", cls.name if hasattr(cls, "name") else cls.__class__.__name__
        )
        description = kwargs.pop(
            "description", cleandoc(cls.__doc__) if cls.__doc__ is not None else ""
        )
        parser = super().construct_argparser(
            name=name, description=description, **kwargs
        )

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


if __name__ == "__main__":
    CropProcessor.main()
