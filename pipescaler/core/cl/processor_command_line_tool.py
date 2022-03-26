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
from typing import Union

from pipescaler.common import CommandLineTool


class ProcessorCommandLineTool(CommandLineTool, ABC):
    @classmethod
    def add_arguments_to_argparser(
        cls,
        parser: Union[ArgumentParser, _SubParsersAction],
    ) -> None:
        super().add_arguments_to_argparser(parser)

        parser.add_argument("infile", type=cls.input_path_arg(), help="input file")
        parser.add_argument("outfile", type=cls.output_path_arg(), help="output file")

    @classmethod
    def main(cls) -> None:
        """Parse arguments, initialize processor, and process file."""
        parser = cls.construct_argparser()
        kwargs = vars(parser.parse_args())
        infile = kwargs.pop("infile")
        outfile = kwargs.pop("outfile")
        processor = cls.processor(**kwargs)
        processor(infile, outfile)

    @classmethod
    @property
    def name(cls) -> str:
        return cls.__name__.rstrip("CommandLineTool")

    @classmethod
    @property
    @abstractmethod
    def processor(cls) -> type:
        raise NotImplementedError()
