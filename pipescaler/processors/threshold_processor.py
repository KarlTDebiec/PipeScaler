#!/usr/bin/env python
#   pipescaler/processors/threshold_processor.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
from __future__ import annotations

from argparse import ArgumentParser
from inspect import cleandoc
from typing import Any, no_type_check

import numba as nb
import numpy as np
from PIL import Image

from pipescaler.core import (
    Processor,
    UnsupportedImageModeError,
    remove_palette_from_image,
)


class ThresholdProcessor(Processor):
    """Converts to black and white using threshold, optionally denoising."""

    def __init__(
        self, threshold: int = 128, denoise: bool = False, **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)

        self.threshold = threshold
        self.denoise = denoise

    def process_file(self, infile: str, outfile: str) -> None:
        # Read image
        input_image = Image.open(infile)
        if input_image.mode == "P":
            input_image = remove_palette_from_image(input_image)
        if input_image.mode != "L":
            raise UnsupportedImageModeError(
                f"Image mode '{input_image.mode}' of image '{infile}'"
                f" is not supported by {type(self)}"
            )

        # Process image
        output_image = input_image.point(lambda p: p > self.threshold and 255)
        if self.denoise:
            output_data = np.array(output_image)
            self.denoise_data(output_data)
            output_image = Image.fromarray(output_data)
        output_image = output_image.convert("L")

        # Write image
        output_image.save(outfile)

    @classmethod
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """
        Constructs argument parser.

        Returns:
            parser (ArgumentParser): Argument parser
        """
        description = kwargs.get("description", cleandoc(cls.__doc__))
        parser = super().construct_argparser(description=description, **kwargs)

        parser.add_argument(
            "--threshold",
            default=128,
            type=int,
            help="threshold differentiating black and white (0-255, default: "
            "%(default)s)",
        )
        parser.add_argument(
            "--denoise",
            default=False,
            type=bool,
            help="Flip color of pixels bordered by less than 5 pixels of "
            "the same color",
        )

        return parser

    @no_type_check
    @staticmethod
    @nb.jit(nopython=True, nogil=True, cache=True, fastmath=True)
    def denoise_data(data: np.ndarray) -> None:
        for x in range(1, data.shape[1] - 1):
            for y in range(1, data.shape[0] - 1):
                slc = data[y - 1 : y + 2, x - 1 : x + 2]
                if data[y, x] == 0:
                    if (slc == 0).sum() < 4:
                        data[y, x] = 255
                else:
                    if (slc == 255).sum() < 4:
                        data[y, x] = 0


if __name__ == "__main__":
    ThresholdProcessor.main()
