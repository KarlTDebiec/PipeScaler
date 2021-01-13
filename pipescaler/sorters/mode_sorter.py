#!/usr/bin/env python
#   pipescaler/sorters/mode_sorter.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from os.path import isfile
from typing import Any, Generator, List, Optional, Union

import numpy as np
from PIL import Image

from pipescaler.common import validate_int, validate_output_path
from pipescaler.core import PipeImage, Sorter


####################################### CLASSES ########################################
class ModeSorter(Sorter):

    # region Builtins

    def __init__(
            self,
            drop_alpha_threshold: Optional[int] = None,
            downstream_stages_for_rgba: Optional[Union[str, List[str]]] = None,
            downstream_stages_for_rgb: Optional[Union[str, List[str]]] = None,
            downstream_stages_for_l: Optional[Union[str, List[str]]] = None,
            **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

        # Store configuration
        if drop_alpha_threshold is None:
            self.drop_alpha_threshold = None
        else:
            self.drop_alpha_threshold = validate_int(
                drop_alpha_threshold, min_value=0, max_value=255
            )
        if isinstance(downstream_stages_for_rgba, str):
            downstream_stages_for_rgba = [downstream_stages_for_rgba]
        self.downstream_stages_for_rgba = downstream_stages_for_rgba
        if isinstance(downstream_stages_for_rgb, str):
            downstream_stages_for_rgb = [downstream_stages_for_rgb]
        self.downstream_stages_for_rgb = downstream_stages_for_rgb
        if isinstance(downstream_stages_for_l, str):
            downstream_stages_for_l = [downstream_stages_for_l]
        self.downstream_stages_for_l = downstream_stages_for_l

        # Prepare description
        desc = f"{self.name} {self.__class__.__name__}"
        desc += f"\n ├─ RGBA"
        if self.downstream_stages_for_rgba is not None:
            if len(self.downstream_stages_for_rgba) >= 2:
                for stage in self.downstream_stages_for_rgba[:-1]:
                    desc += f"\n │   ├─ {stage}"
            desc += f"\n │  └─ {self.downstream_stages_for_rgba[-1]}"
        else:
            desc += f"\n │  └─"
        desc += f"\n ├─ RGB"
        if self.downstream_stages_for_rgb is not None:
            if len(self.downstream_stages_for_rgb) >= 2:
                for stage in self.downstream_stages_for_rgb[:-1]:
                    desc += f"\n │   ├─ {stage}"
            desc += f"\n │  └─ {self.downstream_stages_for_rgb[-1]}"
        else:
            desc += f"\n │  └─"
        desc += f"\n └─ L"
        if self.downstream_stages_for_l is not None:
            if len(self.downstream_stages_for_l) >= 2:
                for stage in self.downstream_stages_for_l[:-1]:
                    desc += f"\n     ├─ {stage}"
            desc += f"\n    └─ {self.downstream_stages_for_l[-1]}"
        else:
            desc += f"\n    └─"
        self.desc = desc

    def __call__(self) -> Generator[PipeImage, PipeImage, None]:
        while True:
            image = yield
            if self.pipeline.verbosity >= 2:
                print(f"{self} sorting: {image.name} ({image.mode})")
            if image.mode == "RGBA":
                if self.drop_alpha_threshold is not None and np.all(
                        np.array(Image.open(image.last))[:, :, 3]
                        >= self.drop_alpha_threshold
                ):
                    outfile = validate_output_path(
                        self.pipeline.get_outfile(image, "RGB")
                    )
                    if not isfile(outfile):
                        if self.pipeline.verbosity >= 2:
                            print(f"{self} dropping alpha: {image.name}")
                        rgba_image = Image.open(image.last)
                        rgba_datum = np.array(rgba_image)
                        rgb_image = Image.fromarray(rgba_datum[:, :, :3])
                        rgb_image.save(outfile)
                    image.log(self.name, outfile)
                    if self.downstream_stages_for_rgb is not None:
                        for stage in self.downstream_stages_for_rgb:
                            self.pipeline.stages[stage].send(image)
                else:
                    if self.downstream_stages_for_rgba is not None:
                        for stage in self.downstream_stages_for_rgba:
                            self.pipeline.stages[stage].send(image)
            elif image.mode == "RGB":
                if self.downstream_stages_for_rgb is not None:
                    for stage in self.downstream_stages_for_rgb:
                        self.pipeline.stages[stage].send(image)
            elif image.mode == "L":
                if self.downstream_stages_for_l is not None:
                    for stage in self.downstream_stages_for_l:
                        self.pipeline.stages[stage].send(image)

    # endregion
