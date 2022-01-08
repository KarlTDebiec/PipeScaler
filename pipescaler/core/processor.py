#!/usr/bin/env python
#   pipescaler/core/processor.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Base class for processors"""
from __future__ import annotations

from argparse import ArgumentParser
from inspect import cleandoc
from typing import Any, List, Optional

from pipescaler.common import CommandLineTool
from pipescaler.core.stage import Stage


class Processor(Stage, CommandLineTool):
    """Base class for processors"""

    def __init__(self, suffix: Optional[str] = None, **kwargs: Any) -> None:
        """
        Validate and store static configuration

        Arguments:
            suffix: Suffix to append to images
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Store configuration
        if suffix is not None:
            self.suffix = suffix
        else:
            self.suffix = self.name

    def __call__(self, infile: str, outfile: str) -> None:
        """
        Read image from infile, process it, and save to outfile

        Arguments:
            infile: Input file path
            outfile: Output file path
        """
        raise NotImplementedError()

    @property
    def inlets(self) -> List[str]:
        """Inlets that flow into stage"""
        return ["inlet"]

    @property
    def outlets(self) -> List[str]:
        """Outlets that flow out of stage"""
        return ["outlet"]

    @classmethod
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """
        Construct argument parser

        Arguments:
            **kwargs: Additional keyword arguments

        Returns:
            parser: Argument parser
        """
        description = kwargs.pop(
            "description", cleandoc(cls.__doc__) if cls.__doc__ is not None else ""
        )
        parser = super().construct_argparser(description=description, **kwargs)

        # Input
        parser.add_argument("infile", type=cls.input_path_arg(), help="input file")
        parser.add_argument("outfile", type=cls.output_path_arg(), help="output file")

        return parser

    @classmethod
    def main(cls) -> None:
        """Parse arguments, initialize processor, and process file"""
        parser = cls.construct_argparser()
        kwargs = vars(parser.parse_args())
        infile = kwargs.pop("infile")
        outfile = kwargs.pop("outfile")
        cls(**kwargs)(infile, outfile)
