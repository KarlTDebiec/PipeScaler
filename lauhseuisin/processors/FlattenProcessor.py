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
class FlattenProcessor(Processor):
    def process_file(self, infile: str, outfile: str) -> None:
        if isfile(outfile):
            return
        print(f"Flattening to '{outfile}'")
        input_data = np.array(Image.open(infile))
        output_data = np.ones_like(input_data) * 255
        output_data[:, :, 0] = 255 - input_data[:, :, 3]
        output_data[:, :, 1] = 255 - input_data[:, :, 3]
        output_data[:, :, 2] = 255 - input_data[:, :, 3]
        output_data[:, :, :3] += input_data[:, :, :3]
        Image.fromarray(output_data).convert("RGB").save(outfile)

    @classmethod
    def get_pipes(cls, **kwargs: Any) -> List[Processor]:
        return [cls(paramstring=f"flatten")]
