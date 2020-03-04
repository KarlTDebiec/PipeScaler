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
from typing import Any, List, no_type_check

import numba as nb
import numpy as np
from PIL import Image

from lauhseuisin.processors import Processor


################################### CLASSES ###################################
class ThresholdProcessor(Processor):

    def __init__(self, threshold: int = 128, denoise: bool = False,
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.threshold = threshold
        self.denoise = denoise

    def process_file(self, infile: str, outfile: str) -> None:
        if isfile(outfile):
            return
        print(f"Processeing to '{outfile}'")
        input_image = Image.open(infile).convert("L").point(
            lambda p: p > self.threshold and 255)
        data = np.array(input_image)
        if self.denoise:
            self.denoise_data(data)
        processed_image = Image.fromarray(data)
        processed_image.save(outfile)

    @classmethod
    def get_pipes(cls, **kwargs: Any) -> List[Processor]:
        thresholds = kwargs.pop("threshold")
        if not isinstance(thresholds, list):
            thresholds = [thresholds]
        denoises = kwargs.pop("denoise")
        if not isinstance(denoises, list):
            denoises = [denoises]

        processors: List[Processor] = []
        for threshold in thresholds:
            for denoise in denoises:
                if denoise:
                    paramstring = f"threshold-{threshold}-denoise"
                else:
                    paramstring = f"threshold-{threshold}"
                processors.append(cls(
                    threshold=threshold,
                    denoise=denoise,
                    paramstring=paramstring,
                    **kwargs))
        return processors

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
