#!/usr/bin/env python
#   pipescaler/core/cl/processor_command_line_tool.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
from __future__ import annotations

from abc import ABC, abstractmethod
from argparse import ArgumentParser, _SubParsersAction
from inspect import cleandoc
from typing import Any, Union

from pipescaler.common import CommandLineTool
from pipescaler.core import Processor


class ProcessorCommandLineTool(CommandLineTool, ABC):
    @classmethod
    def add_arguments_to_argparser(
        cls,
        parser: Union[ArgumentParser, _SubParsersAction],
    ) -> None:
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: Nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        parser.add_argument("infile", type=cls.input_path_arg(), help="input file")
        parser.add_argument("outfile", type=cls.output_path_arg(), help="output file")

    @classmethod
    def main(cls) -> None:
        parser = cls.construct_argparser()
        kwargs = vars(parser.parse_args())
        cls.process(**kwargs)

    @classmethod
    def process(cls, infile: str, outfile: str, **kwargs: Any) -> None:
        processor = cls.processor(**kwargs)
        processor(infile, outfile)

    @classmethod
    @property
    def description(cls) -> str:
        """Long description of this tool displayed below usage."""
        if cls.processor.__doc__:
            return cleandoc(cls.processor.__doc__)
        return ""

    @classmethod
    @property
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser."""
        return cls.__name__.removesuffix("CommandLineTool").lower()

    @classmethod
    @property
    @abstractmethod
    def processor(cls) -> type[Processor]:
        """Type of processor wrapped by command-line tool."""
        raise NotImplementedError()
