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

from typing import Any, Generator, List, Optional, Union

from pipescaler.core import PipeImage, Sorter


####################################### CLASSES ########################################
class ModeSorter(Sorter):

    # region Builtins

    def __init__(
        self,
        downstream_stages_for_rgba: Optional[Union[str, List[str]]] = None,
        downstream_stages_for_rgb: Optional[Union[str, List[str]]] = None,
        downstream_stages_for_l: Optional[Union[str, List[str]]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

        # Store configuration
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
            desc += f"\n │   └─ {self.downstream_stages_for_rgba[-1]}"
        desc += f"\n ├─ RGB"
        if self.downstream_stages_for_rgb is not None:
            if len(self.downstream_stages_for_rgb) >= 2:
                for stage in self.downstream_stages_for_rgb[:-1]:
                    desc += f"\n │   ├─ {stage}"
            desc += f"\n │   └─ {self.downstream_stages_for_rgb[-1]}"
        desc += f"\n └─ L"
        if self.downstream_stages_for_l is not None:
            if len(self.downstream_stages_for_l) >= 2:
                for stage in self.downstream_stages_for_l[:-1]:
                    desc += f"\n     ├─ {stage}"
            desc += f"\n     └─ {self.downstream_stages_for_l[-1]}"
        self.desc = desc

    def __call__(self) -> Generator[PipeImage, PipeImage, None]:
        while True:
            image = yield
            if self.pipeline.verbosity >= 2:
                print(f"{self} sorting: {image.name} ({image.mode})")
            if image.mode == "RGBA":
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
