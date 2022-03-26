#!/usr/bin/env python
#   pipescaler/scripts/process.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
from __future__ import annotations

from argparse import ArgumentParser, _SubParsersAction
from typing import Union

from pipescaler.common import CommandLineTool
from pipescaler.scripts import processors


class ProcessCommandLineTool(CommandLineTool):
    processors = {
        processor.name: processor
        for processor in map(processors.__dict__.get, processors.__all__)
    }

    @classmethod
    def add_arguments_to_argparser(
        cls,
        parser: Union[ArgumentParser, _SubParsersAction],
    ) -> None:
        super().add_arguments_to_argparser(parser)

        subparsers = parser.add_subparsers(dest="processor")
        for name in sorted(cls.processors):
            cls.processors[name].construct_argparser(parser=subparsers)

    @classmethod
    def main(cls) -> None:
        """Parse arguments, initialize processor, and process file"""
        parser = cls.construct_argparser()
        kwargs = vars(parser.parse_args())
        processor = cls.processors[kwargs.pop("processor")]
        processor.process(**kwargs)


if __name__ == "__main__":
    ProcessCommandLineTool.main()
