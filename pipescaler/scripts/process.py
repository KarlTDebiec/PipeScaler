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
from typing import Optional, Union

from pipescaler.common import CommandLineTool
from pipescaler.scripts.processors import CropCommandLineTool


class ProcessCommandLineTool(CommandLineTool):
    @classmethod
    def construct_argparser(
        cls,
        parser: Optional[_SubParsersAction] = None,
    ) -> Union[ArgumentParser, _SubParsersAction]:
        """Construct argument parser.

        Arguments:
            **kwargs: Additional keyword arguments
        Returns:
            parser: Argument parser
        """
        parser = super().construct_argparser(parser=parser)

        subparsers = parser.add_subparsers()
        CropCommandLineTool.construct_argparser(parser=subparsers)

        return parser

    @classmethod
    def main(cls) -> None:
        """Parse arguments, initialize processor, and process file"""
        parser = cls.construct_argparser()
        kwargs = vars(parser.parse_args())


if __name__ == "__main__":
    ProcessCommandLineTool.main()
