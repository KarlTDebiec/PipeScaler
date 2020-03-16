#!python
# -*- coding: utf-8 -*-
#   lauhseuisin/processors/ImageMagickProcessor.py
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
from typing import Any, List

from lauhseuisin.processors.Processor import Processor


################################### CLASSES ###################################
class ImageMagickProcessor(Processor):
    executable_name = "convert"

    def __init__(self, extension: str, resize: Any = False,
                 remove_infile: bool = False, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.extension = extension
        self.remove_infile = remove_infile
        self.resize = resize

    def process_file(self, infile: str, outfile: str) -> None:
        if isfile(outfile):
            return
        print(f"Processing to '{outfile}'")
        if self.resize:
            command = f"{self.executable} " \
                      f"-resize {self.resize[0]}x{self.resize[1]} " \
                      f"{infile} " \
                      f"{outfile}"
        else:
            command = f"{self.executable} " \
                      f"{infile} " \
                      f"{outfile}"
        print(command)
        Popen(command, shell=True, close_fds=True).wait()
        if self.remove_infile:
            remove(infile)

    @classmethod
    def get_pipes(cls, **kwargs: Any) -> List[Processor]:
        return [cls(extension=kwargs.pop("extension", "bmp"),
                    remove_infile=kwargs.pop("remove_infile", False),
                    resize=kwargs.pop("resize", False),
                    paramstring="",
                    **kwargs)]
