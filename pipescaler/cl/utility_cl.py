#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for PipeScaler utilities."""
from __future__ import annotations

from argparse import ArgumentParser, _SubParsersAction
from typing import Type, Union

from pipescaler.cl import utilities
from pipescaler.common import CommandLineTool


class UtilityCL(CommandLineTool):
    """Command-line interface for PipeScaler utilities."""

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

        subparsers = parser.add_subparsers(dest="utility")
        # noinspection PyTypeChecker
        for name in sorted(cls.utilities):
            cls.utilities[name].construct_argparser(parser=subparsers)

    @classmethod
    def main(cls) -> None:
        """Parse arguments, initialize processor, and process file."""
        parser = cls.construct_argparser()
        kwargs = vars(parser.parse_args())
        utility = cls.utilities[kwargs.pop("processor")]
        utility.process(**kwargs)

    @classmethod
    @property
    def description(cls) -> str:
        """Long description of this tool displayed below usage."""
        return "Runs utilities."

    @classmethod
    @property
    def help(cls) -> str:
        """Short description of this tool used when it is a subparser."""
        return "run utilities"

    @classmethod
    @property
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser."""
        return cls.__name__.removesuffix("CL").lower()

    @classmethod
    @property
    def utilities(cls) -> dict[str:Type]:
        """Names and types of utilities wrapped by command-line tool."""
        return {
            utility.name: utility
            for utility in map(utilities.__dict__.get, utilities.__all__)
        }


if __name__ == "__main__":
    UtilityCL.main()
