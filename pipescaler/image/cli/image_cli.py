#  Copyright 2020-2023 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for PipeScaler image operations."""
from __future__ import annotations

from argparse import ArgumentParser
from typing import Type, Union

from pipescaler.common import CommandLineInterface, set_logging_verbosity
from pipescaler.image.cli.image_processors_cli import ImageProcessorsCli
from pipescaler.image.cli.image_utilities_cli import ImageUtilitiesCli


class ImageCli(CommandLineInterface):
    """Command-line interface for PipeScaler image operations."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser) -> None:
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: Nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        subparsers = parser.add_subparsers(
            dest="subcommand", help="subcommand", required=True
        )
        for name in sorted(cls.subcommands()):
            cls.subcommands()[name].argparser(subparsers=subparsers)

    @classmethod
    def description(cls) -> str:
        """Long description of this tool displayed below usage."""
        return "Image operations."

    @classmethod
    def help(cls) -> str:
        """Short description of this tool used when it is a subparser."""
        return "image operations"

    @classmethod
    def main(cls) -> None:
        """Execute from command line."""
        parser = cls.argparser()
        kwargs = vars(parser.parse_args())
        set_logging_verbosity(kwargs.pop("verbosity", 1))

        subcommand_name = kwargs.pop("subcommand")
        subcommand_cli_class = cls.subcommands()[subcommand_name]
        subcommand_cli_class.main_internal(**kwargs)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser."""
        return "image"

    @classmethod
    def subcommands(
        cls,
    ) -> dict[str, Union[Type[ImageProcessorsCli], Type[ImageUtilitiesCli]]]:
        """Names and types of tools wrapped by command-line interface."""
        return {tool.name(): tool for tool in [ImageProcessorsCli, ImageUtilitiesCli]}
