#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for PipeScaler image operations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pipescaler.common import CommandLineInterface

from .image_mergers_cli import ImageMergersCli
from .image_processors_cli import ImageProcessorsCli
from .image_splitters_cli import ImageSplittersCli
from .image_utilities_cli import ImageUtilitiesCli

if TYPE_CHECKING:
    from argparse import ArgumentParser


class ImageCli(CommandLineInterface):
    """Command-line interface for PipeScaler image operations."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
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
    def description(cls) -> str:
        """Long description of this tool displayed below usage."""
        return "Image operations."

    @classmethod
    def help(cls) -> str:
        """Short description of this tool used when it is a subparser."""
        return "image operations"

    @classmethod
    def _main(cls, **kwargs: Any):
        """Execute with provided keyword arguments."""
        subcommand_name = kwargs.pop("subcommand")
        subcommand_cli_class = cls.subcommands()[subcommand_name]
        subcommand_cli_class._main(**kwargs)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser."""
        return "image"

    @classmethod
    def subcommands(
        cls,
    ) -> dict[
        str,
        type[ImageMergersCli]
        | type[ImageProcessorsCli]
        | type[ImageSplittersCli]
        | type[ImageUtilitiesCli],
    ]:
        """Names and types of tools wrapped by command-line interface."""
        return {
            ImageMergersCli.name(): ImageMergersCli,
            ImageProcessorsCli.name(): ImageProcessorsCli,
            ImageSplittersCli.name(): ImageSplittersCli,
            ImageUtilitiesCli.name(): ImageUtilitiesCli,
        }
