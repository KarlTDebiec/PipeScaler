#!/usr/bin/env python
#   pipescaler/processors/PotraceProcessor.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
################################### MODULES ###################################
from __future__ import annotations

from argparse import ArgumentParser
from os import remove
from os.path import splitext
from subprocess import Popen
from typing import Any

from pipescaler.processors.Processor import Processor


################################### CLASSES ###################################
class PotraceProcessor(Processor):

    # region Builtins

    def __init__(self, blacklevel: float = 0.3, alphamax: float = 1.34,
                 opttolerance: float = 0.2, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.blacklevel = blacklevel
        self.alphamax = alphamax
        self.opttolerance = opttolerance

    # endregion

    # region Properties

    @property
    def desc(self) -> str:
        """str: Description"""
        if not hasattr(self, "_desc"):
            return f"potrace-{self.blacklevel:4.2f}-" \
                   f"{self.alphamax:4.2f}-{self.opttolerance:3.1f}"
        return self._desc

    # endregion

    # region Methods

    def process_file_in_pipeline(self, infile: str, outfile: str) -> None:
        self.process_file(infile, outfile, self.pipeline.verbosity,
                          blacklevel=self.blacklevel, alphamax=self.alphamax,
                          opttolerance=self.opttolerance)

    # endregion

    # region Class Methods

    @classmethod
    def construct_argparser(cls) -> ArgumentParser:
        """
        Constructs argument parser

        Returns:
            parser (ArgumentParser): Argument parser
        """
        parser = super().construct_argparser(description=__doc__)

        parser.add_argument(
            "-k", "--blacklevel",
            default=0.3,
            type=float,
            help="black/white cutoff in input file (default: 0.3)")
        parser.add_argument(
            "-a", "--alphamax",
            default=1.34,
            type=float,
            help="corner threshold parameter (default: 1.34)")
        parser.add_argument(
            "-O", "--opttolerance",
            default=0.2,
            type=float,
            help="curve optimization tolerance (default: 0.2)")

        return parser

    @classmethod
    def process_file(cls, infile: str, outfile: str, verbosity: int = 1,
                     **kwargs: Any):
        blacklevel = kwargs.get("blacklevel")
        alphamax = kwargs.get("alphamax")
        opttolerance = kwargs.get("opttolerance")

        # TODO: Use temporary files

        # Convert to bmp; potrace does not accept png
        bmpfile = f"{splitext(infile)[0]}.bmp"
        command = f"convert " \
                  f"{infile} " \
                  f"{bmpfile}"
        if verbosity >= 1:
            print(command)
        Popen(command, shell=True, close_fds=True).wait()

        # trace
        svgfile = f"{splitext(outfile)[0]}.svg"
        command = f"potrace " \
                  f"{bmpfile} " \
                  f"-b svg " \
                  f"-k {blacklevel} " \
                  f"-a {alphamax} " \
                  f"-O {opttolerance} " \
                  f"-o {svgfile}"
        if verbosity >= 1:
            print(command)
        Popen(command, shell=True, close_fds=True).wait()

        # Rasterize svg to png
        command = f"convert " \
                  f"{svgfile} " \
                  f"{outfile}"
        if verbosity >= 1:
            print(command)
        Popen(command, shell=True, close_fds=True).wait()

        # Clean up
        remove(bmpfile)
        remove(svgfile)

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    PotraceProcessor.main()
