#!python
# -*- coding: utf-8 -*-
#   lauhseuisin/processors/WaifuProcessor.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
################################### MODULES ###################################
from __future__ import annotations

from os import remove
from os.path import isfile
from subprocess import Popen
from tempfile import NamedTemporaryFile
from typing import Any, List, Optional, IO

from PIL import Image

from lauhseuisin.processors.Processor import Processor


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
        image = Image.open(infile)
        original_size = image.size
        tempfile: Optional[IO[bytes]] = None
        if original_size[0] < 200 or original_size[1] < 200:
            tempfile = NamedTemporaryFile(delete=False, suffix=".png")
            expanded_image = Image.new(
                image.mode, (max(200, original_size[0]),
                             max(200, original_size[1])))
            expanded_image.paste(
                image, (0, 0, original_size[0], original_size[1]))
            expanded_image.save(tempfile)
            tempfile.close()
            intermediate_infile = tempfile.name
        else:
            intermediate_infile = infile
        print(f"Processing to '{outfile}'")
        command = f"{self.executable} " \
                  f"-t {self.imagetype} " \
                  f"-s {self.scale} " \
                  f"-n {self.noise} " \
                  f"-i {intermediate_infile} " \
                  f"-o {outfile}"
        print(command)
        Popen(command, shell=True, close_fds=True).wait()
        if tempfile is not None:
            Image.open(outfile).crop(
                (0, 0, original_size[0] * self.scale,
                 original_size[1] * self.scale)).save(outfile)
            remove(tempfile.name)

    @classmethod
    def get_pipes(cls, **kwargs: Any) -> List[Processor]:
        processors: List[Processor] = []
        imagetypes = kwargs.pop("imagetype")
        if not isinstance(imagetypes, list):
            imagetypes = [imagetypes]
        scales = kwargs.pop("scale")
        if not isinstance(scales, list):
            scales = [scales]
        noises = kwargs.pop("noise")
        if not isinstance(noises, list):
            noises = [noises]
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
