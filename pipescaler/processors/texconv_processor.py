#!/usr/bin/env python
#   pipescaler/processors/texconv_processor.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from argparse import ArgumentParser
from subprocess import Popen
from typing import Any, Optional
from os.path import isfile, dirname
from pipescaler.core import Processor
from pipescaler.common import validate_output_path

####################################### CLASSES ########################################
class TexconvProcessor(Processor):

    # region Builtins

    def __init__(
            self,
            sepalpha: bool = False,
            filetype: Optional[str] = None,
            format: Optional[str] = None,
            **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

        self.sepalpha = sepalpha
        self.filetype = filetype
        self.format = format
        self.desc = self.name

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
                sepalpha=self.sepalpha,
                filetype=self.filetype,
                format=self.format,
            )
        image.log(self.name, outfile)

    # endregion

    @classmethod
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """
        Constructs argument parser.

        Returns:
            parser (ArgumentParser): Argument parser
        """
        description = kwargs.get("description", __doc__.strip())
        parser = super().construct_argparser(description=description, **kwargs)

        parser.add_argument(
            "--sepalpha",
            action="store_true",
            help="resize/generate mips alpha channel separately from color channels"
        )
        parser.add_argument(
            "--filetype",
            type=str,
            help="output file type",
        )
        parser.add_argument(
            "--format",
            type=str,
            help="output format",
        )

        return parser

    @classmethod
    def process_file(
            cls, infile: str, outfile: str, verbosity: int = 1, **kwargs: Any
    ) -> None:
        sepalpha = kwargs.get("sepalpha", False)
        filetype = kwargs.get("filetype")
        format = kwargs.get("format")
        outfile = dirname(infile)

        command = f"texconv.exe"
        if sepalpha:
            command = f"{command} -sepalpha"
        if filetype:
            command = f"{command} -ft {filetype}"
        if format:
            command = f"{command} -f {format}"
        command = f"{command} \"{infile}\" -o \"{outfile}\""

        if verbosity >= 1:
            print(command)
        Popen(command, shell=True, close_fds=True).wait()


######################################### MAIN #########################################
if __name__ == "__main__":
    TexconvProcessor.main()
