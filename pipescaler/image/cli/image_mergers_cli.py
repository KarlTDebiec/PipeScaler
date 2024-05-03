#!/usr/bin/env python
#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for PipeScaler ImageMergers."""
from __future__ import annotations

from argparse import ArgumentParser
from typing import Any, Type

from pipescaler.common import CommandLineInterface
from pipescaler.image.cli import mergers
from pipescaler.image.core.cli import ImageMergerCli


class ImageMergersCli(CommandLineInterface):
    """Command-line interface for PipeScaler ImageMergers."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser) -> None:
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: Nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        subparsers = parser.add_subparsers(
            dest="merger",
            help="merger",
            required=True,
        )
        for name in sorted(cls.mergers()):
            cls.mergers()[name].argparser(subparsers=subparsers)

    @classmethod
    def description(cls) -> str:
        """Long description of this tool displayed below usage."""
        return "Merges images."

    @classmethod
    def help(cls) -> str:
        """Short description of this tool used when it is a subparser."""
        return "merge image"

    @classmethod
    def main_internal(cls, **kwargs: Any) -> None:
        """Execute with provided keyword arguments."""
        merger_name = kwargs.pop("merger")
        merger_cli_cls = cls.mergers()[merger_name]
        merger_cli_cls.main_internal(**kwargs)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser."""
        return "merge"

    @classmethod
    def mergers(cls) -> dict[str, Type[ImageMergerCli]]:
        """Names and types of mergers wrapped by command-line interface."""
        return {
            merger.name(): merger
            for merger in map(mergers.__dict__.get, mergers.__all__)
            if isinstance(merger, type) and issubclass(merger, ImageMergerCli)
        }


if __name__ == "__main__":
    ImageMergersCli.main()
