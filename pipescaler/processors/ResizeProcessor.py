#!/usr/bin/env python
#   pipescaler/processors/ResizeProcessor.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
################################### MODULES ###################################
from __future__ import annotations

from typing import Any

import numpy as np
from PIL import Image

from pipescaler.processors.Processor import Processor


################################### CLASSES ###################################
class ResizeProcessor(Processor):

    def __init__(self, scale: float, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.scale = scale
        self.desc = f"resize-{scale}"

    def process_file_in_pipeline(self, infile: str, outfile: str) -> None:
        self.process_file(infile, outfile, self.scale, self.pipeline.verbosity)

    @classmethod
    def process_file(cls, infile: str, outfile: str, scale: float,
                     verbosity: int) -> None:
        # Load and scale image
        input_image = Image.open(infile)
        size = (int(np.round(input_image.size[0] * scale)),
                int(np.round(input_image.size[1] * scale)))
        output_image = input_image.convert("RGB").resize(
            size, resample=Image.LANCZOS)

        # Combine R, G, and B from RGB with A from RGBA
        if input_image.mode == "RGBA":
            rgba_image = input_image.resize(
                size, resample=Image.LANCZOS)
            merged_data = np.zeros((size[1], size[0], 4), np.uint8)
            merged_data[:, :, :3] = np.array(output_image)
            merged_data[:, :, 3] = np.array(rgba_image)[:, :, 3]
            output_image = Image.fromarray(merged_data)

        # Save image
        output_image.save(outfile)
