#!/usr/bin/env python
#   pipescaler/splitter/normal_splitter.py
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
class NormalSplitter(Splitter):

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
                print(f"    splitting: {image.name}")
            rgb = Image.open(image.last)
            r_outfile = validate_output_path(self.pipeline.get_outfile(image, "R"))
            g_outfile = validate_output_path(self.pipeline.get_outfile(image, "G"))
            b_outfile = validate_output_path(self.pipeline.get_outfile(image, "B"))

            if not isfile(r_outfile):
                if self.pipeline.verbosity >= 3:
                    print(f"    saving red to '{r_outfile}'")
                Image.fromarray(np.array(rgb)[:, :, 0]).save(r_outfile)
            image.log(self.name, r_outfile)
            if self.downstream_stages_for_rgb is not None:
                for pipe in self.downstream_stages_for_rgb:
                    self.pipeline.stages[pipe].send(image)

            if not isfile(g_outfile):
                if self.pipeline.verbosity >= 3:
                    print(f"    saving green to '{g_outfile}'")
                Image.fromarray(np.array(rgb)[:, :, 1]).save(g_outfile)
            image.log(self.name, g_outfile)
            if self.downstream_stages_for_rgb is not None:
                for pipe in self.downstream_stages_for_rgb:
                    self.pipeline.stages[pipe].send(image)

            if not isfile(b_outfile):
                if self.pipeline.verbosity >= 3:
                    print(f"    saving blue to '{b_outfile}'")
                Image.fromarray(np.array(rgb)[:, :, 2]).save(b_outfile)
            image.log(self.name, b_outfile)
            if self.downstream_stages_for_rgb is not None:
                for pipe in self.downstream_stages_for_rgb:
                    self.pipeline.stages[pipe].send(image)

    # endregion
