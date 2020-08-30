#!/usr/bin/env python
#   pipescaler/splitter/alpha_splitter.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from typing import Any, Generator, Optional

import numpy as np
from PIL import Image

from pipescaler.common import validate_output_path
from pipescaler.core import PipeImage, Splitter


####################################### CLASSES ########################################
class AlphaSplitter(Splitter):

    # region Builtins

    def __init__(
        self,
        downstream_stage_for_rgb: Optional[str] = None,
        downstream_stage_for_a: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

        # Store configuration
        if isinstance(downstream_stage_for_rgb, str):
            downstream_stage_for_rgb = [downstream_stage_for_rgb]
        self.downstream_stage_for_rgb = downstream_stage_for_rgb
        if isinstance(downstream_stage_for_a, str):
            downstream_stage_for_a = [downstream_stage_for_a]
        self.downstream_stage_for_a = downstream_stage_for_a

    def __call__(self) -> Generator[PipeImage, PipeImage, None]:
        while True:
            image = yield
            if self.pipeline.verbosity >= 2:
                print(f"{self} splitting: {image.name}")
            if image.mode == "RGBA":
                rgb_outfile = validate_output_path(
                    self.pipeline.get_outfile(image, "RGB")
                )
                a_outfile = validate_output_path(self.pipeline.get_outfile(image, "A"))

                if self.pipeline.verbosity >= 3:
                    print(f"saving RGB file to '{rgb_outfile}'")
                Image.fromarray(np.array(image.image)[:, :, :3]).save(rgb_outfile)
                image.log(self.name, rgb_outfile)
                if self.downstream_stage_for_rgb is not None:
                    self.pipeline.stages[self.downstream_stage_for_rgb].send(image)

                if self.pipeline.verbosity >= 3:
                    print(f"saving A file to '{a_outfile}'")
                Image.fromarray(np.array(image.image)[:, :, 3]).save(a_outfile)
                image.log(self.name, a_outfile)
                if self.downstream_stage_for_a is not None:
                    self.pipeline.stages[self.downstream_stage_for_a].send(image)

    # endregion
