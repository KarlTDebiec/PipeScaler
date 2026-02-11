#!/usr/bin/env python
#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for PipeScaler ImageSplitters."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pipescaler.common import CommandLineInterface
from pipescaler.image.core.cli import ImageSplitterCli

from . import splitters

if TYPE_CHECKING:
    from argparse import ArgumentParser


class ImageSplittersCli(CommandLineInterface):
    """Command-line interface for PipeScaler ImageSplitters."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: Nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        subparsers = parser.add_subparsers(
            dest="splitter",
            help="splitter",
            required=True,
        )
        for name in sorted(cls.splitters()):
            cls.splitters()[name].argparser(subparsers=subparsers)

    @classmethod
    def description(cls) -> str:
        """Long description of this tool displayed below usage."""
        return "Splits images."

    @classmethod
    def help(cls) -> str:
        """Short description of this tool used when it is a subparser."""
        return "split image"

    @classmethod
    def _main(cls, **kwargs: Any):
        """Execute with provided keyword arguments."""
        splitter_name = kwargs.pop("splitter")
        splitter_cli_cls = cls.splitters()[splitter_name]
        splitter_cli_cls._main(**kwargs)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser."""
        return "split"

    @classmethod
    def splitters(cls) -> dict[str, type[ImageSplitterCli]]:
        """Names and types of splitters wrapped by command-line interface."""
        return {
            splitter.name(): splitter
            for splitter in map(splitters.__dict__.get, splitters.__all__)
            if isinstance(splitter, type) and issubclass(splitter, ImageSplitterCli)
        }


if __name__ == "__main__":
    ImageSplittersCli.main()
