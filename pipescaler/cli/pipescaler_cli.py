#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Command line interface for PipeScaler."""
from __future__ import annotations

from argparse import ArgumentParser, _SubParsersAction
from typing import Any, Type, Union

from pipescaler.cli.process_cli import ProcessCli
from pipescaler.cli.run_cli import RunCli
from pipescaler.cli.utility_cli import UtilityCli
from pipescaler.common import CommandLineInterface


class PipeScalerCli(CommandLineInterface):
    """Command line interface for PipeScaler."""

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
        ProcessCli.construct_argparser(parser=subparsers)
        RunCli.construct_argparser(parser=subparsers)
        UtilityCli.construct_argparser(parser=subparsers)

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
    def subtools(cls) -> dict[str, Type[CommandLineInterface]]:
        """Names and types of tools wrapped by command line interface."""
        return {tool.name: tool for tool in [ProcessCli, RunCli, UtilityCli]}


if __name__ == "__main__":
    PipeScalerCli.main()
