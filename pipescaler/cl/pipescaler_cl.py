#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for PipeScaler."""
from __future__ import annotations

from argparse import ArgumentParser, _SubParsersAction
from pprint import pprint
from typing import Any, Type, Union

from pipescaler.cl.process_cl import ProcessCL
from pipescaler.cl.run_cl import RunCL
from pipescaler.cl.utility_cl import UtilityCL
from pipescaler.common import CommandLineTool


class PipeScalerCL(CommandLineTool):
    """Command-line interface for PipeScaler."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def __call__(self) -> None:
        pass

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

        subparsers = parser.add_subparsers(dest="subtool")
        ProcessCL.construct_argparser(parser=subparsers)
        RunCL.construct_argparser(parser=subparsers)
        UtilityCL.construct_argparser(parser=subparsers)

    @classmethod
    def main(cls) -> None:
        """Parse arguments, initialize processor, and process file."""
        parser = cls.construct_argparser()
        kwargs = vars(parser.parse_args())
        cls.main2(**kwargs)

    @classmethod
    def main2(cls, **kwargs: Any) -> None:
        subtool = cls.subtools[kwargs.pop("subtool")]
        subtool.main2(**kwargs)

    @classmethod
    @property
    def subtools(cls) -> dict[str, Type[CommandLineTool]]:
        """Names and types of tools wrapped by command-line tool."""
        return {tool.name: tool for tool in [ProcessCL, RunCL, UtilityCL]}


if __name__ == "__main__":
    PipeScalerCL.main()
