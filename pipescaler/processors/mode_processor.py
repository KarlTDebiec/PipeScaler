#!/usr/bin/env python
#   pipescaler/processors/mode_processor.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from os.path import isfile
from typing import Any, List, Optional, Union

import numpy as np
from PIL import Image, ImageColor

from pipescaler.common import validate_output_path
from pipescaler.core import PipeImage, Processor


####################################### CLASSES ########################################
class ModeProcessor(Processor):

    # region Builtins

    def __init__(
        self, mode: str = "RGB", background_color="#000000", **kwargs: Any,
    ) -> None:

        super().__init__(**kwargs)

        self.mode = mode
        self.background_color = ImageColor.getrgb(background_color)
        self.desc = f"{self.name}_{mode}"

    # endregion

    # region Methods

    def process_file_in_pipeline(self, image: PipeImage) -> None:
        infile = image.last
        outfile = validate_output_path(self.pipeline.get_outfile(image, self.suffix))
        if not isfile(outfile):
            self.process_file(
                infile,
                outfile,
                self.pipeline.verbosity,
                mode=self.mode,
                background_color=self.background_color,
            )
        image.log(self.name, outfile)

    # endregion

    # region Class Methods

    @classmethod
    def process_file(
        cls, infile: str, outfile: str, verbosity: int = 1, **kwargs: Any
    ) -> None:
        mode = kwargs.get("mode", "RGB").upper()
        background_color = kwargs.get("background_color", ImageColor.getrgb("#000000"))
        input_image = Image.open(infile)

        if input_image.mode == mode:
            input_image.save(outfile)
        else:
            output_image = Image.new("RGBA", input_image.size, background_color)
            output_image.paste(input_image)
            if mode == "RGBA":
                pass
            elif mode == "RGB":
                output_image = output_image.convert("RGB")
            elif mode == "L":
                output_image = output_image.convert("L")
        output_image.save(outfile)

    # endregion
