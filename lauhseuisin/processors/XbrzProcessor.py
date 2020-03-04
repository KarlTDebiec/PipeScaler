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
from subprocess import Popen
from typing import Any, List

from lauhseuisin.processors import Processor


################################### CLASSES ###################################
class XbrzProcessor(Processor):
    executable_name = "xbrzscale"

    def __init__(self, scale: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.scale = scale

    def process_file(self, infile: str, outfile: str) -> None:
        if isfile(outfile):
            return
        print(f"Processing to '{outfile}'")
        command = f"{self.executable} " \
                  f"{self.scale} " \
                  f"{infile} " \
                  f"{outfile}"
        print(command)
        Popen(command, shell=True, close_fds=True).wait()

    @classmethod
    def get_pipes(cls, **kwargs: Any) -> List[Processor]:
        processors: List[Processor] = []
        scales = kwargs.pop("scale")
        for scale in scales:
            processors.append(cls(
                scale=scale,
                paramstring=f"xbrz-"
                            f"{scale}",
                **kwargs))
        return processors
