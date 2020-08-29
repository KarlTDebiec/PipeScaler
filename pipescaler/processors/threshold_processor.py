#!/usr/bin/env python
#   pipescaler/processors/threshold_processor.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from argparse import ArgumentParser
from typing import Any, no_type_check

import numba as nb
import numpy as np
from PIL import Image

from pipescaler.core import Processor


####################################### CLASSES ########################################
class ThresholdProcessor(Processor):

    # region Builtins

    def __init__(
        self, threshold: int = 128, denoise: bool = False, **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)

        self.threshold = threshold
        self.denoise = denoise

    # endregion

    # region Properties

    @property
    def desc(self) -> str:
        """str: Description"""
        if not hasattr(self, "_desc"):
            if self.denoise:
                return f"threshold-{self.threshold}-{self.denoise}"
            else:
                return f"threshold-{self.threshold}"
        return self._desc

    # endregion

    # region Methods

    def process_file_in_pipeline(self, infile: str, outfile: str) -> None:
        self.process_file(
            infile,
            outfile,
            self.pipeline.verbosity,
            threshold=self.threshold,
            denoise=self.denoise,
        )

    # endregion

    # region Class Methods

    @classmethod
    def construct_argparser(cls) -> ArgumentParser:
        """
        Constructs argument parser.

        Returns:
            parser (ArgumentParser): Argument parser
        """
        parser = super().construct_argparser(description=__doc__)

        parser.add_argument(
            "--threshold",
            default=128,
            type=int,
            help="threshold differentiating black and white (0-255, default: "
            "%(default)s)",
        )
        parser.add_argument(
            "--denoise",
            default=True,
            type=bool,
            help="Flip color of pixels bordered by less than 5 pixels of "
            "the same color",
        )

        return parser

    @classmethod
    def process_file(
        cls, infile: str, outfile: str, verbosity: int = 1, **kwargs: Any
    ) -> None:
        threshold = kwargs.get("threshold")
        denoise = kwargs.get("denoise")
        input_image = Image.open(infile)

        output_image = input_image.convert("L").point(lambda p: p > threshold and 255)
        if denoise:
            output_data = np.array(output_image)
            cls.denoise_data(output_data)
            output_image = Image.fromarray(output_data)

        output_image.save(outfile)

    # endregion

    # region Static Methods

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

    # endregion


######################################### MAIN #########################################
if __name__ == "__main__":
    ThresholdProcessor.main()
