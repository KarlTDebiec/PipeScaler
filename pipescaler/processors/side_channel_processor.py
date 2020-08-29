#!/usr/bin/env python
#   pipescaler/processors/side_channel_processor.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from os.path import basename, isfile, join, splitext
from shutil import copyfile
from typing import Any

from pipescaler.common import validate_input_path
from pipescaler.core import Processor


####################################### CLASSES ########################################
class SideChannelProcessor(Processor):

    # region Builtins

    def __init__(self, input_directory: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.input_directory = input_directory

    # endregion

    # region Properties

    @property
    def desc(self) -> str:
        """str: Description"""
        if not hasattr(self, "_desc"):
            return "sidechannel"
        return self._desc

    @property
    def input_directory(self) -> str:
        """str: Input directory"""
        if not hasattr(self, "_input_directory"):
            raise ValueError()
        return self._input_directory

    @input_directory.setter
    def input_directory(self, value: str) -> None:
        self._input_directory = validate_input_path(
            value, file_ok=False, directory_ok=True
        )

    # endregion

    # region Methods

    def get_outfile(self, infile: str) -> str:
        original_name = self.get_original_name(infile)
        desc_so_far = splitext(basename(infile))[0].replace(original_name, "")
        if isfile(f"{self.input_directory}/{original_name}.png"):
            outfile = f"{desc_so_far}_{self.desc}.png".lstrip("_")
            outfile = f"{self.pipeline.wip_directory}/{original_name}/" f"{outfile}"
        else:
            outfile = None

        return outfile

    def process_file_in_pipeline(self, infile: str, outfile: str) -> None:
        original_name = self.get_original_name(infile)
        extension = self.get_extension(infile)
        sidechannel_file = join(self.input_directory, f"{original_name}.{extension}")
        if isfile(sidechannel_file):
            self.process_file(sidechannel_file, outfile, self.pipeline.verbosity)

    # endregion

    # region Class Methods

    @classmethod
    def process_file(
        cls, infile: str, outfile: str, verbosity: int = 1, **kwargs
    ) -> None:
        if verbosity >= 1:
            print(f"cp {infile} {outfile}")
        copyfile(infile, outfile)

    # endregion
