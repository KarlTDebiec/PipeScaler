#!/usr/bin/env python
#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for PipeScaler ImageProcessors."""
from __future__ import annotations

from argparse import ArgumentParser
from typing import Any, Type

from pipescaler.common import CommandLineInterface
from pipescaler.image.cli import processors
from pipescaler.image.core.cli import ImageProcessorCli


class ImageProcessorsCli(CommandLineInterface):
    """Command-line interface for PipeScaler ImageProcessors."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser) -> None:
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: Nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        subparsers = parser.add_subparsers(
            dest="processor",
            help="processor",
            required=True,
        )
        for name in sorted(cls.processors()):
            cls.processors()[name].argparser(subparsers=subparsers)

    @classmethod
    def description(cls) -> str:
        """Long description of this tool displayed below usage."""
        return "Processes images."

    @classmethod
    def help(cls) -> str:
        """Short description of this tool used when it is a subparser."""
        return "process image"

    @classmethod
    def _main(cls, **kwargs: Any) -> None:
        """Execute with provided keyword arguments."""
        processor_name = kwargs.pop("processor")
        processor_cli_cls = cls.processors()[processor_name]
        processor_cli_cls._main(**kwargs)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser."""
        return "process"

    @classmethod
    def processors(cls) -> dict[str, Type[ImageProcessorCli]]:
        """Names and types of processors wrapped by command-line interface."""
        return {
            processor.name(): processor
            for processor in map(processors.__dict__.get, processors.__all__)
            if isinstance(processor, type) and issubclass(processor, ImageProcessorCli)
        }


if __name__ == "__main__":
    ImageProcessorsCli.main()
