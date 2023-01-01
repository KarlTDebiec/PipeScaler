#!/usr/bin/env python
#  Copyright 2020-2023 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for PipeScaler."""
from __future__ import annotations

from argparse import ArgumentParser
from typing import Any, Type

from pipescaler.common import CommandLineInterface
from pipescaler.image.cli.image_processors_cli import ImageProcessorsCli
from pipescaler.image.cli.utilities_cli import UtilitiesCli


class PipeScalerCli(CommandLineInterface):
    """Command-line interface for PipeScaler."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser) -> None:
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: Nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        subparsers = parser.add_subparsers(dest="action", help="action", required=True)
        ImageProcessorsCli.argparser(subparsers=subparsers)
        UtilitiesCli.argparser(subparsers=subparsers)

    @classmethod
    def execute(cls, **kwargs: Any) -> None:
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: Command-line arguments
        """
        sub_cli = cls.subcommands()[kwargs.pop("action")]
        sub_cli.execute(**kwargs)

    @classmethod
    def subcommands(cls) -> dict[str, Type[CommandLineInterface]]:
        """Names and types of tools wrapped by command-line interface."""
        return {
            tool.name(): tool for tool in [ImageProcessorsCli, UtilitiesCli]  # type: ignore
        }


if __name__ == "__main__":
    PipeScalerCli.main()
