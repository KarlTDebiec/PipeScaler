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
class WaifuProcessor(Processor):
    executable_name = "waifu2x"

    def __init__(self, imagetype: str, scale: str, noise: str,
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.imagetype = imagetype
        self.scale = scale
        self.noise = noise

    def process_file(self, infile: str, outfile: str) -> None:
        if isfile(outfile):
            return
        print(f"Processing to '{outfile}'")
        command = f"{self.executable} " \
                  f"-t {self.imagetype} " \
                  f"-s {self.scale} " \
                  f"-n {self.noise} " \
                  f"-i {infile} " \
                  f"-o {outfile}"
        print(command)
        Popen(command, shell=True, close_fds=True).wait()

    @classmethod
    def get_pipes(cls, **kwargs: Any) -> List[Processor]:
        processors: List[Processor] = []
        imagetypes = kwargs.pop("imagetype")
        scales = kwargs.pop("scale")
        noises = kwargs.pop("noise")
        for imagetype in imagetypes:
            for scale in scales:
                for noise in noises:
                    processors.append(cls(
                        imagetype=imagetype,
                        scale=scale,
                        noise=noise,
                        paramstring=f"waifu-"
                                    f"{imagetype}-"
                                    f"{scale}-"
                                    f"{noise}",
                        **kwargs))
        return processors
