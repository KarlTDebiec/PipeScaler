#!/usr/bin/env python
#   pipescaler/processors/xbrz_processor.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from argparse import ArgumentParser
from os.path import isfile
from subprocess import Popen
from typing import Any

from pipescaler.common import validate_output_path
from pipescaler.core import PipeImage, Processor


####################################### CLASSES ########################################
class XbrzProcessor(Processor):

    # region Builtins

    def __init__(self, scale: int = 4, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.scale = scale
        self.suffix = f"xbrz-{self.scale}"

        # Prepare description
        desc = (
            f"{self.name} {self.__class__.__name__} (scale={self.scale})"
        )
        if self.downstream_stages is not None:
            if len(self.downstream_stages) >= 2:
                for stage in self.downstream_stages[:-1]:
                    desc += f"\n ├─ {stage}"
            desc += f"\n └─ {self.downstream_stages[-1]}"
        self.desc = desc

    # endregion

    # region Methods

    def process_file_in_pipeline(self, image: PipeImage) -> None:
        infile = image.last
        outfile = validate_output_path(self.pipeline.get_outfile(image, self.suffix))
        if not isfile(outfile):
            self.process_file(
                infile,
                outfile,
                self.pipeline.verbosity,
                scale=self.scale,
            )
        image.log(self.name, outfile)

    # endregion

    # region Class Methods

    @classmethod
    def construct_argparser(cls) -> ArgumentParser:
        """
        Constructs argument parser.

        Returns:
            parser (ArgumentParser): Argument parser
        """
        parser = super().construct_argparser(description=__doc__)

        # Input
        parser.add_argument(
            "--scale",
            default=2,
            type=int,
            help="factor by which to scale height and width (2-6, default: "
                 "%(default)s)",
        )

        return parser

    @classmethod
    def process_file(
            cls, infile: str, outfile: str, verbosity: int = 1, **kwargs: Any
    ) -> None:
        scale = kwargs.get("scale", 2)

        command = f"xbrzscale " f"{scale} " f"{infile} " f"{outfile}"
        if verbosity >= 1:
            print(f"    {command}")
        Popen(command, shell=True, close_fds=True).wait()

    # endregion


######################################### MAIN #########################################
if __name__ == "__main__":
    XbrzProcessor.main()
