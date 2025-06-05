#!/usr/bin/env python
#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for PipeScaler image utilities."""
from __future__ import annotations

from argparse import ArgumentParser
from typing import Any, Type

from pipescaler.common import CommandLineInterface
from pipescaler.core.cli import UtilityCli
from pipescaler.image.cli import utilities


class ImageUtilitiesCli(CommandLineInterface):
    """Command-line interface for PipeScaler image utilities."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser) -> None:
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: Nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        subparsers = parser.add_subparsers(
            dest="utility",
            help="utility",
            required=True,
        )
        for name in sorted(cls.utilities()):
            cls.utilities()[name].argparser(subparsers=subparsers)

    @classmethod
    def description(cls) -> str:
        """Long description of this tool displayed below usage."""
        return "Runs image utilities."

    @classmethod
    def help(cls) -> str:
        """Short description of this tool used when it is a subparser."""
        return "run image utility"

    @classmethod
    def _main(cls, **kwargs: Any) -> None:
        """Execute with provided keyword arguments."""
        utility_name = kwargs.pop("utility")
        utility_cli_cls = cls.utilities()[utility_name]
        utility_cli_cls._main(**kwargs)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser."""
        return "utility"

    @classmethod
    def utilities(cls) -> dict[str, Type[UtilityCli]]:
        """Names and types of utilities wrapped by command-line interface."""
        return {
            utility.name(): utility
            for utility in map(utilities.__dict__.get, utilities.__all__)
            if isinstance(utility, type) and issubclass(utility, UtilityCli)
        }


if __name__ == "__main__":
    ImageUtilitiesCli.main()
