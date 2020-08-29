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

from os import listdir
from os.path import isfile, join
from shutil import copyfile
from typing import Any

from pipescaler.common import get_name, validate_input_path, validate_output_path
from pipescaler.core import PipeImage, Processor


####################################### CLASSES ########################################
class SideChannelProcessor(Processor):

    # region Builtins

    def __init__(self, directory: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.directory = validate_input_path(
            directory, file_ok=False, directory_ok=True
        )
        self.infiles = {
            get_name(f): f
            for f in [
                validate_input_path(f, default_directory=self.directory)
                for f in listdir(self.directory)
                if f != ".DS_Store"
            ]
        }

        # Prepare description
        desc = f"{self.name} {self.__class__.__name__} ({self.directory})"
        if self.downstream_stages is not None:
            if len(self.downstream_stages) >= 2:
                for stage in self.downstream_stages[:-1]:
                    desc += f"\n ├─ {stage}"
            desc += f"\n └─ {self.downstream_stages[-1]}"
        self.desc = desc

    # endregion

    # region Methods

    def process_file_in_pipeline(self, image: PipeImage) -> None:
        if image.name in self.infiles:
            infile = self.infiles[image.name]
            outfile = validate_output_path(
                self.pipeline.get_outfile(image, self.suffix)
            )
            self.process_file(infile, outfile, self.pipeline.verbosity)
            image.log(self.name, outfile)

    # endregion

    # region Class Methods

    @classmethod
    def process_file(
        cls, infile: str, outfile: str, verbosity: int = 1, **kwargs
    ) -> None:
        if verbosity >= 3:
            print(f"cp {infile} {outfile}")
        copyfile(infile, outfile)

    # endregion
