#!python
# -*- coding: utf-8 -*-
#   LauhSeuiSin.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
################################### MODULES ###################################
from __future__ import annotations

from os.path import isfile
from typing import Any, List

import numpy as np
from PIL import Image

from lauhseuisin.processors import Processor


################################### CLASSES ###################################
class ResizeProcessor(Processor):

    def __init__(self, scale: float, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.scale = scale

    def process_file(self, infile: str, outfile: str) -> None:
        if isfile(outfile):
            return
        print(f"Processeing to '{outfile}'")
        input_image = Image.open(infile)
        output_image = input_image.resize((
            int(np.round(input_image.size[0] * self.scale)),
            int(np.round(input_image.size[1] * self.scale))))
        output_image.save(outfile)

    @classmethod
    def get_pipes(cls, **kwargs: Any) -> List[Processor]:
        scales = kwargs.pop("scale")
        if not isinstance(scales, list):
            scales = [scales]

        processors: List[Processor] = []
        for scale in scales:
            processors.append(cls(
                scale=scale,
                paramstring=f"resize-{scale:7.5f}",
                **kwargs))
        return processors

