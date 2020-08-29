#!/usr/bin/env python
#   pipescaler/processors/resize_processor.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from typing import Any

import numpy as np
from PIL import Image

from pipescaler.core import Processor


####################################### CLASSES ########################################
class ResizeProcessor(Processor):

    # region Builtins

    def __init__(self, scale: float, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.scale = scale

    # endregion

    # region Properties

    @property
    def desc(self) -> str:
        """str: Description"""
        if not hasattr(self, "_desc"):
            return f"resize-{self.scale}"
        return self._desc

    # endregion

    # region Methods

    def process_file_in_pipeline(self, infile: str, outfile: str) -> None:
        self.process_file(infile, outfile, self.pipeline.verbosity, scale=self.scale)

    # endregion

    # region Class Methods

    @classmethod
    def process_file(
        cls, infile: str, outfile: str, verbosity: int = 1, **kwargs
    ) -> None:
        scale = kwargs.get("scale", 2)

        # Load and scale image
        input_image = Image.open(infile)
        size = (
            int(np.round(input_image.size[0] * scale)),
            int(np.round(input_image.size[1] * scale)),
        )
        output_image = input_image.convert("RGB").resize(size, resample=Image.LANCZOS)

        # Combine R, G, and B from RGB with A from RGBA
        if input_image.mode == "RGBA":
            rgba_image = input_image.resize(size, resample=Image.LANCZOS)
            merged_data = np.zeros((size[1], size[0], 4), np.uint8)
            merged_data[:, :, :3] = np.array(output_image)
            merged_data[:, :, 3] = np.array(rgba_image)[:, :, 3]
            output_image = Image.fromarray(merged_data)

        # Save image
        output_image.save(outfile)

    # endregion
