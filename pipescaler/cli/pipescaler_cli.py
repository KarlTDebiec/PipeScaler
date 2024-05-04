#!/usr/bin/env python
#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for PipeScaler."""
from __future__ import annotations

from argparse import ArgumentParser
from typing import Any, Type

from pipescaler.common import CommandLineInterface
from pipescaler.image.cli import ImageCli


class PipeScalerCli(CommandLineInterface):
    """Command-line interface for PipeScaler."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser) -> None:
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: Nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        subparsers = parser.add_subparsers(
            dest="subcommand",
            help="subcommand",
            required=True,
        )
        for name in sorted(cls.subcommands()):
            cls.subcommands()[name].argparser(subparsers=subparsers)

    @classmethod
    def main_internal(cls, **kwargs: Any) -> None:
        """Execute with provided keyword arguments."""
        subcommand_name = kwargs.pop("subcommand")
        subcommand_cli_class = cls.subcommands()[subcommand_name]
        subcommand_cli_class.main_internal(**kwargs)

    @classmethod
    def subcommands(cls) -> dict[str, Type[ImageCli]]:
        """Names and types of tools wrapped by command-line interface."""
        return {
            ImageCli.name(): ImageCli,
        }


if __name__ == "__main__":
    PipeScalerCli.main()
