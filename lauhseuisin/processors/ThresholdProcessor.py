#!python
# -*- coding: utf-8 -*-
#   lauhseuisin/processors/ThresholdProcessor.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
################################### MODULES ###################################
from __future__ import annotations

from argparse import ArgumentParser
from typing import Any, no_type_check

import numba as nb
import numpy as np
from PIL import Image

from lauhseuisin.processors.Processor import Processor


################################### CLASSES ###################################
class ThresholdProcessor(Processor):

    def __init__(self, threshold: int = 128, denoise: bool = False,
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.threshold = threshold
        self.denoise = denoise
        self.desc = f"threshold-{self.threshold}"
        if self.denoise:
            self.desc = f"{self.desc}-{self.denoise}"

    def process_file_in_pipeline(self, infile: str, outfile: str) -> None:
        self.process_file(infile, outfile, self.threshold, self.denoise,
                          self.pipeline.verbosity)

    # region Public Class Methods

    @classmethod
    def construct_argparser(cls) -> ArgumentParser:
        """
        Constructs argument parser

        Returns:
            parser (ArgumentParser): Argument parser
        """
        parser = super().construct_argparser(description=__doc__)

        parser.add_argument(
            "-t", "--threshold",
            default=128,
            dest="threshold",
            type=int,
            help="threshold differentiating black and white (0-255)")
        parser.add_argument(
            "-d", "--denoise",
            default=True,
            dest="denoise",
            type=bool,
            help="Switch color of pixels bordered by less than 5 pixels of "
                 "the same color")

        return parser

    @classmethod
    def process_file(cls, infile: str, outfile: str, threshold: int,
                     denoise: bool, verbosity:int):
        input_image = Image.open(infile)

        output_image = input_image.convert("L").point(
            lambda p: p > threshold and 255)
        if denoise:
            output_data = np.array(output_image)
            cls.denoise_data(output_data)
            output_image = Image.fromarray(output_data)

        output_image.save(outfile)

    # endregion

    @no_type_check
    @staticmethod
    @nb.jit(nopython=True, nogil=True, cache=True, fastmath=True)
    def denoise_data(data: np.ndarray) -> None:
        for x in range(1, data.shape[1] - 1):
            for y in range(1, data.shape[0] - 1):
                slc = data[y - 1:y + 2, x - 1:x + 2]
                if data[y, x] == 0:
                    if (slc == 0).sum() < 4:
                        data[y, x] = 255
                else:
                    if (slc == 255).sum() < 4:
                        data[y, x] = 0


#################################### MAIN #####################################
if __name__ == "__main__":
    ThresholdProcessor.main()
