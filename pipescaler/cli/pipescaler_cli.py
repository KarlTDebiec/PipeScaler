#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for PipeScaler."""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Any

from pipescaler.common.cli import CommandLineInterface
from pipescaler.common.cli.entry_points import get_cli_commands
from pipescaler.image.cli import ImageCli

__all__ = ["PipeScalerCli"]


class PipeScalerCli(CommandLineInterface):
    """Command-line interface for PipeScaler."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: Nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        # Subcommands
        subparsers = parser.add_subparsers(
            dest=cls.subcommand_dest(),
            help="subcommand",
            required=True,
        )
        for name in sorted(cls.subcommands()):
            cls.subcommands()[name].argparser(subparsers=subparsers)

    @classmethod
    def subcommands(cls) -> dict[str, type[CommandLineInterface]]:
        """Names and types of tools wrapped by command-line interface.

        Returns:
            mapping of command names to their CLI classes
        """
        return get_cli_commands(
            {ImageCli.name(): ImageCli},
            group="pipescaler.cli.commands",
            base_class=CommandLineInterface,
        )

    @classmethod
    def _main(cls, **kwargs: Any):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: additional options forwarded to the selected implementation
        """
        subcommand_name = kwargs.pop(cls.subcommand_dest())
        subcommand_cli_class = cls.subcommands()[subcommand_name]
        subcommand_cli_class._main(**kwargs)


if __name__ == "__main__":
    PipeScalerCli.main()
