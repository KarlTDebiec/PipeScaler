#!python
# -*- coding: utf-8 -*-
#   lauhseuisin/processors/ResizeProcessor.py
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

from lauhseuisin.processors.Processor import Processor


################################### CLASSES ###################################
class ResizeProcessor(Processor):

    def __init__(self, scale: float, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.scale = scale
        self.desc = f"resize-{scale}"

    def process_file(self, infile: str, outfile: str) -> None:
        input_image = Image.open(infile)
        output_image = input_image.resize((
            int(np.round(input_image.size[0] * self.scale)),
            int(np.round(input_image.size[1] * self.scale))),
            resample=Image.LANCZOS)
        output_image.save(outfile)
