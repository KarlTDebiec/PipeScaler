#!/usr/bin/env python
#   pipescaler/processors/resize_processor.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from argparse import ArgumentParser
from typing import Any

import numpy as np
from PIL import Image

from pipescaler.common import validate_float, validate_str
from pipescaler.core import PipeImage, Processor


####################################### CLASSES ########################################
class ResizeProcessor(Processor):
    resample_methods = {
        "bicubic": Image.BICUBIC,
        "bilinear": Image.BILINEAR,
        "lanczos": Image.LANCZOS,
        "nearest": Image.NEAREST,
    }

    # region Builtins

    def __init__(self, scale: float, resample: str = "lanczos", **kwargs: Any) -> None:
        super().__init__(**kwargs)

        # Store configuration
        self.scale = validate_float(scale, min_value=0)
        self.resample = validate_str(resample, options=self.resample_methods.keys())

    def __call__(self, infile: str, outfile: str, verbosity: int = 1) -> None:
        self.process_file(
            infile,
            outfile,
            verbosity=verbosity,
            scale=self.scale,
            resample=self.resample,
        )

    # endregion

    # region Properties

    @property
    def inlets(self):
        return ["inlet"]

    @property
    def outlets(self):
        return ["outlet"]

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
            default=2,
            type=cls.float_arg(min_value=0),
            help="scaling factor (default: %(default)s)",
        )
        # TODO: Create cls.str_dict and convert key to value here rather than later
        parser.add_argument(
            "--resample",
            default="lanczos",
            type=cls.str_arg(options=cls.resample_methods.keys()),
            help="background color (default: %(default)s)",
        )

        return parser

    @classmethod
    def process_file(
        cls, infile: str, outfile: str, verbosity: int = 1, **kwargs
    ) -> None:
        scale = kwargs.get("scale", 2)
        resample = cls.resample_methods[kwargs.get("resample", "lanczos")]

        # Load and scale image
        input_image = Image.open(infile)
        size = (
            int(np.round(input_image.size[0] * scale)),
            int(np.round(input_image.size[1] * scale)),
        )
        output_image = input_image.convert("RGB").resize(size, resample=resample)

        # Combine R, G, and B from RGB with A from RGBA
        # TODO: Figure out why this is done, and write it down this time
        if input_image.mode == "RGBA":
            rgba_image = input_image.resize(size, resample=resample)
            merged_data = np.zeros((size[1], size[0], 4), np.uint8)
            merged_data[:, :, :3] = np.array(output_image)
            merged_data[:, :, 3] = np.array(rgba_image)[:, :, 3]
            output_image = Image.fromarray(merged_data)

        # Save image
        output_image.save(outfile)

    # endregion
