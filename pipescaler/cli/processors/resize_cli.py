#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Command line interface for ResizeProcessor."""
from __future__ import annotations

from argparse import ArgumentParser
from typing import Type

from pipescaler.core.cli import ProcessorCli
from pipescaler.core.image import Processor
from pipescaler.image.processors import ResizeProcessor


class ResizeCli(ProcessorCli):
    """Command line interface for ResizeProcessor."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser) -> None:
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: Nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        required = cls.get_required_arguments_group(parser)
        required.add_argument(
            "--scale",
            required=True,
            type=cls.float_arg(min_value=0),
            help="scaling factor",
        )

        optional = cls.get_optional_arguments_group(parser)
        optional.add_argument(
            "--resample",
            default="lanczos",
            type=cls.str_arg(options=ResizeProcessor.resample_methods.keys()),
            help="Resampling method (default: %(default)s)",
        )

    @classmethod
    def processor(cls) -> Type[Processor]:
        """Type of processor wrapped by command line interface."""
        return ResizeProcessor


if __name__ == "__main__":
    ResizeCli.main()
