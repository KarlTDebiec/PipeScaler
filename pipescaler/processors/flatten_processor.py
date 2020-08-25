#!/usr/bin/env python
#   pipescaler/processors/flatten_processor.py
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

from pipescaler.processors.processor import Processor


################################### CLASSES ###################################
class FlattenProcessor(Processor):

    # region Properties

    @property
    def desc(self) -> str:
        """str: Description"""
        if not hasattr(self, "_desc"):
            return "flatten"
        return self._desc

    # endregion

    # region Class Methods

    @classmethod
    def process_file(cls, infile: str, outfile: str, verbosity: int = 1,
                     **kwargs: Any) -> None:
        input_datum = np.array(Image.open(infile))

        output_datum = np.ones_like(input_datum) * 255
        output_datum[:, :, 0] = 255 - input_datum[:, :, 3]
        output_datum[:, :, 1] = 255 - input_datum[:, :, 3]
        output_datum[:, :, 2] = 255 - input_datum[:, :, 3]
        output_datum[:, :, :3] += input_datum[:, :, :3]
        output_image = Image.fromarray(output_datum).convert("RGB")

        output_image.save(outfile)

    # endregion
