#!/usr/bin/env python
#   pipescaler/scripts/apng_creator.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
""""""
####################################### MODULES ########################################
from __future__ import annotations

from argparse import ArgumentParser
from os import remove
from subprocess import Popen
from tempfile import NamedTemporaryFile
from typing import Any, List

from PIL import Image

from pipescaler.common import CLTool, validate_output_path


####################################### CLASSES ########################################
class APNGCreator(CLTool):

    # region Builtins

    def __init__(self, infiles: List[str], outfile: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.infiles = infiles
        self.outfile = outfile

    def __call__(self, **kwargs: Any) -> None:
        images = []
        sizes = []
        for infile in self.infiles:
            image = Image.open(infile)
            images.append(image)
            sizes.append(image.size)

        tempfiles = []
        for i, image in enumerate(images):
            if image.size != max(sizes):
                image = image.resize(max(sizes), resample=Image.NEAREST)
            tempfiles.append(NamedTemporaryFile(delete=False, suffix=".png"))
            tempfiles[-1].close()
            image.save(tempfiles[-1].name)
        command = (
            f"apngasm "
            f"-o {self.outfile} "
            f"{' '.join([t.name for t in tempfiles])} "
            f"-d 500 "
            f"--force"
        )
        print(command)
        Popen(command, shell=True, close_fds=True).wait()
        for tempfile in tempfiles:
            remove(tempfile.name)

    # endregion

    # region Properties

    @property
    def infiles(self) -> List[str]:
        """str: Directory from which to load image files"""
        if not hasattr(self, "_infiles"):
            self._infiles = []
        return self._infiles

    @infiles.setter
    def infiles(self, value: List[str]) -> None:
        self._infiles = list(map(validate_output_path, value))

    @property
    def outfile(self) -> str:
        """str: Output animated png file"""
        if not hasattr(self, "_outfile"):
            self._outfile = validate_output_path("out.png")
        return self._outfile

    @outfile.setter
    def outfile(self, value: str):
        self._outfile = validate_output_path(value)

    # endregion

    # region Class Methods

    @classmethod
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """
        Constructs argument parser.

        Args:
            kwargs (Any): Additional keyword arguments

        Returns:
            ArgumentParser: Argument parser
        """
        parser = super().construct_argparser(description=__doc__.strip(), **kwargs)

        # Input
        parser.add_argument(
            "-i",
            "--infiles",
            nargs="+",
            type=cls.input_path_arg(file_ok=True, directory_ok=True),
            help="input files or directory",
        )
        # Labels

        # Operations
        # Show labels
        # Show size

        # Output
        parser.add_argument(
            "-o",
            "--outfile",
            default="out.png",
            type=cls.output_path_arg(),
            help="output animated png",
        )

        return parser

    # endregion


######################################### MAIN #########################################
if __name__ == "__main__":
    APNGCreator.main()
