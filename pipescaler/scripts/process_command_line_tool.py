#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
from __future__ import annotations

from argparse import ArgumentParser, _SubParsersAction
from typing import Type, Union

from pipescaler.common import CommandLineTool
from pipescaler.core import Processor
from pipescaler.scripts import processors


class ProcessCommandLineTool(CommandLineTool):
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

        subparsers = parser.add_subparsers(dest="processor")
        for name in sorted(cls.processors):
            cls.processors[name].construct_argparser(parser=subparsers)

    @classmethod
    def main(cls) -> None:
        """Parse arguments, initialize processor, and process file."""
        parser = cls.construct_argparser()
        kwargs = vars(parser.parse_args())
        processor = cls.processors[kwargs.pop("processor")]
        processor.process(**kwargs)

    @classmethod
    @property
    def processors(cls) -> dict[str : Type[Processor]]:
        """Names and Types of processors wrapped by command-line tool."""
        return {
            processor.name: processor
            for processor in map(processors.__dict__.get, processors.__all__)
        }


if __name__ == "__main__":
    ProcessCommandLineTool.main()
