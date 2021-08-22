#!/usr/bin/env python
#   pipescaler/core/processor.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
""""""
from __future__ import annotations

from abc import abstractmethod
from argparse import ArgumentParser
from typing import Any, List, Optional

from pipescaler.common import CLTool
from pipescaler.core.stage import Stage


class Processor(Stage, CLTool):

    # region Builtins

    def __init__(self, suffix: Optional[str] = None, **kwargs: Any) -> None:
        """
        Validates and stores static configuration.

        Arguments:
            suffix (Optional[str]): suffix to append to images
            kwargs (Any): Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Store configuration
        if suffix is not None:
            self.suffix = suffix
        else:
            self.suffix = self.name

    def __call__(self, infile: str, outfile: str) -> None:
        """
        Processes infile and writes the resulting output to outfile.

        Arguments:
            infile (str): Input file
            outfile (str): Output file
        """
        self.process_file(infile, outfile)

    # endregion

    # region Properties

    @property
    def inlets(self) -> List[str]:
        return ["inlet"]

    @property
    def outlets(self) -> List[str]:
        return ["outlet"]

    # endregion

    # region Methods

    @abstractmethod
    def process_file(cls, infile: str, outfile: str) -> None:
        raise NotImplementedError()

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
        description = kwargs.pop("description", __doc__.strip())
        parser = super().construct_argparser(description=description, **kwargs)

        # Input
        parser.add_argument("infile", type=cls.input_path_arg(), help="input file")
        parser.add_argument("outfile", type=cls.output_path_arg(), help="output file")

        return parser

    @classmethod
    def main(cls) -> None:
        """Parses arguments, initializes processor, and processes file."""
        parser = cls.construct_argparser()
        kwargs = vars(parser.parse_args())
        infile = kwargs.pop("infile")
        outfile = kwargs.pop("outfile")
        cls(**kwargs)(infile, outfile)

    # endregion
