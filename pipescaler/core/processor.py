#!/usr/bin/env python
#   pipescaler/core/processor.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
""""""
####################################### MODULES ########################################
from __future__ import annotations

from abc import abstractmethod
from argparse import ArgumentParser
from typing import Any, Optional

from pipescaler.common import CLTool
from pipescaler.core.stage import Stage


####################################### CLASSES ########################################
class Processor(Stage, CLTool):

    # region Builtins

    def __init__(self, suffix: Optional[str] = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        # Store configuration
        if suffix is not None:
            self.suffix = suffix
        else:
            self.suffix = self.name

    def __call__(
        self, inlet: str, outlet: str, verbosity: int = 1, **kwargs: Any
    ) -> None:
        self.process_file(inlet, outlet, verbosity=verbosity, **kwargs)

    # endregion

    # region Properties

    @property
    def inlets(self):
        return ["default"]

    @property
    def outlets(self):
        return ["default"]

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
        """Parses and validates arguments, passes them to process_file."""
        parser = cls.construct_argparser()
        kwargs = vars(parser.parse_args())
        cls.process_file(**kwargs)

    @classmethod
    @abstractmethod
    def process_file(
        cls, infile: str, outfile: str, verbosity: int = 1, **kwargs: Any
    ) -> None:
        raise NotImplementedError()

    # endregion
