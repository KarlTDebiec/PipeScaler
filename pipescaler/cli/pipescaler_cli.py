#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Command line interface for PipeScaler."""
from __future__ import annotations

from argparse import ArgumentParser, _SubParsersAction
from typing import Any, Type, Union

from pipescaler.cli.processors_cli import ProcessorsCli
from pipescaler.cli.utilities_cli import UtilitiesCli
from pipescaler.common import CommandLineInterface


class PipeScalerCli(CommandLineInterface):
    """Command line interface for PipeScaler."""

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

        subparsers = parser.add_subparsers(dest="sub_cli")
        ProcessorsCli.construct_argparser(parser=subparsers)
        UtilitiesCli.construct_argparser(parser=subparsers)

    @classmethod
    def execute(cls, **kwargs: Any) -> None:
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: Command-line arguments
        """
        sub_cli = cls.sub_clis[kwargs.pop("sub_cli")]
        sub_cli.execute(**kwargs)

    @classmethod
    @property
    def sub_clis(cls) -> dict[str, Type[CommandLineInterface]]:
        """Names and types of tools wrapped by command line interface."""
        return {tool.name: tool for tool in [ProcessorsCli, UtilitiesCli]}


if __name__ == "__main__":
    PipeScalerCli.main()
