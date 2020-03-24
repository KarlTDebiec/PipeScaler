#!python
#   lauhseuisin/processors/FlattenProcessor.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
################################### MODULES ###################################
from __future__ import annotations

import numpy as np
from PIL import Image

from lauhseuisin.processors.Processor import Processor


################################### CLASSES ###################################
class FlattenProcessor(Processor):
    desc = "flatten"

    def process_file_in_pipeline(self, infile: str, outfile: str) -> None:
        self.process_file(infile, outfile)

    @classmethod
    def process_file(cls, infile: str, outfile: str, verbosity: int) -> None:
        input_data = np.array(Image.open(infile))

        output_data = np.ones_like(input_data) * 255
        output_data[:, :, 0] = 255 - input_data[:, :, 3]
        output_data[:, :, 1] = 255 - input_data[:, :, 3]
        output_data[:, :, 2] = 255 - input_data[:, :, 3]
        output_data[:, :, :3] += input_data[:, :, :3]
        output_image = Image.fromarray(output_data).convert("RGB")

        output_image.save(outfile)
