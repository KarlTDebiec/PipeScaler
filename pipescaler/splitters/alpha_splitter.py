#!/usr/bin/env python
#   pipescaler/splitter/alpha_splitter.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from os.path import isfile
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
        downstream_stages_for_rgb: Optional[str] = None,
        downstream_stages_for_a: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

        # Store configuration
        if isinstance(downstream_stages_for_rgb, str):
            downstream_stages_for_rgb = [downstream_stages_for_rgb]
        self.downstream_stages_for_rgb = downstream_stages_for_rgb
        if isinstance(downstream_stages_for_a, str):
            downstream_stages_for_a = [downstream_stages_for_a]
        self.downstream_stages_for_a = downstream_stages_for_a

        # Prepare description
        desc = f"{self.name} {self.__class__.__name__}"
        if self.downstream_stages_for_rgb is not None:
            desc += f"\n ├─ RGB"
            if len(self.downstream_stages_for_rgb) >= 2:
                for stage in self.downstream_stages_for_rgb[:-1]:
                    desc += f"\n │  ├─ {stage}"
            desc += f"\n │  └─ {self.downstream_stages_for_rgb[-1]}"
        if self.downstream_stages_for_a is not None:
            desc += f"\n └─ A"
            if len(self.downstream_stages_for_a) >= 2:
                for stage in self.downstream_stages_for_a[:-1]:
                    desc += f"\n    ├─ {stage}"
            desc += f"\n    └─ {self.downstream_stages_for_a[-1]}"
        self.desc = desc

    def __call__(self) -> Generator[PipeImage, PipeImage, None]:
        while True:
            image = yield
            if self.pipeline.verbosity >= 2:
                print(f"  {self}")
            if image.mode == "RGBA":
                rgba = Image.open(image.last)
                rgb_outfile = validate_output_path(
                    self.pipeline.get_outfile(image, "RGB")
                )
                a_outfile = validate_output_path(self.pipeline.get_outfile(image, "A"))

                if not isfile(rgb_outfile):
                    if self.pipeline.verbosity >= 3:
                        print(f"    saving RGB to '{rgb_outfile}'")
                    Image.fromarray(np.array(rgba)[:, :, :3]).save(rgb_outfile)
                image.log(self.name, rgb_outfile)
                if self.downstream_stages_for_rgb is not None:
                    for pipe in self.downstream_stages_for_rgb:
                        self.pipeline.stages[pipe].send(image)

                if not isfile(a_outfile):
                    if self.pipeline.verbosity >= 3:
                        print(f"    saving alpha to '{a_outfile}'")
                    Image.fromarray(np.array(rgba)[:, :, 3]).save(a_outfile)
                image.log(self.name, a_outfile)
                if self.downstream_stages_for_a is not None:
                    for pipe in self.downstream_stages_for_a:
                        self.pipeline.stages[pipe].send(image)
            else:
                raise ValueError()

    # endregion
