#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for PipeScaler Processors."""
from __future__ import annotations

from argparse import ArgumentParser, _SubParsersAction
from typing import Any, Type, Union

from pipescaler.cl import processors
from pipescaler.common import CommandLineTool
from pipescaler.core import Processor


class ProcessCL(CommandLineTool):
    """Command-line interface for PipeScaler Processors."""

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

        subparsers = parser.add_subparsers(dest="subparser")
        # noinspection PyTypeChecker
        for name in sorted(cls.processors):
            cls.processors[name].construct_argparser(parser=subparsers)

    @classmethod
    def main(cls) -> None:
        """Parse arguments, initialize processor, and process file."""
        parser = cls.construct_argparser()
        kwargs = vars(parser.parse_args())
        cls.main2(**kwargs)

    @classmethod
    def main2(cls, **kwargs: Any) -> None:
        processor = cls.processors[kwargs.pop("subparser")]
        processor.process(**kwargs)

    @classmethod
    @property
    def description(cls) -> str:
        """Long description of this tool displayed below usage."""
        return "Processes images."

    @classmethod
    @property
    def help(cls) -> str:
        """Short description of this tool used when it is a subparser."""
        return "process image"

    @classmethod
    @property
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser."""
        return cls.__name__.removesuffix("CL").lower()

    @classmethod
    @property
    def processors(cls) -> dict[str, Type[Processor]]:
        """Names and types of processors wrapped by command-line tool."""
        return {
            processor.name: processor
            for processor in map(processors.__dict__.get, processors.__all__)
        }


if __name__ == "__main__":
    ProcessCL.main()
