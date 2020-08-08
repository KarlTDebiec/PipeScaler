#!/usr/bin/env python
#   pipescaler/processors/SideChannelProcessor.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
################################### MODULES ###################################
from __future__ import annotations

from os.path import basename, expandvars, isfile, splitext
from shutil import copyfile
from typing import Any

from pipescaler.processors.Processor import Processor


################################### CLASSES ###################################
class SideChannelProcessor(Processor):

    def __init__(self, input_directory: str, desc: str = "sidechannel",
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.input_directory = expandvars(input_directory)
        self.desc = desc

    def get_outfile(self, infile: str) -> str:
        original_name = self.get_original_name(infile)
        desc_so_far = splitext(basename(infile))[0].replace(original_name, "")
        if isfile(f"{self.input_directory}/{original_name}.png"):
            outfile = f"{desc_so_far}_{self.desc}.png".lstrip("_")
            outfile = f"{self.pipeline.wip_directory}/{original_name}/" \
                      f"{outfile}"
        else:
            outfile = None

        return outfile

    def process_file_in_pipeline(self, infile: str, outfile: str) -> None:
        original_name = self.get_original_name(infile)
        sidechannel_file = f"{self.input_directory}/{original_name}.png"
        if isfile(sidechannel_file):
            self.process_file(sidechannel_file, outfile,
                              self.pipeline.verbosity)

    @classmethod
    def process_file(cls, sidechannel_file: str, outfile: str,
                     verbosity: int) -> None:
        if verbosity >= 1:
            print(f"cp {sidechannel_file} {outfile}")
        copyfile(sidechannel_file, outfile)
