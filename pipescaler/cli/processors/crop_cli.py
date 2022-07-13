#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Command line interface for CropProcessor."""
from __future__ import annotations

from argparse import ArgumentParser
from typing import Type

from pipescaler.core.cli import ProcessorCli
from pipescaler.core.image import Processor
from pipescaler.image.processors import CropProcessor


class CropCli(ProcessorCli):
    """Command line interface for CropProcessor."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser) -> None:
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: Nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        required = cls.get_required_arguments_group(parser)
        required.add_argument(
            "--pixels",
            metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"),
            nargs=4,
            required=True,
            type=cls.int_arg(min_value=1),
            help="number of pixels to remove from each side",
        )

    @classmethod
    def processor(cls) -> Type[Processor]:
        """Type of processor wrapped by command line interface."""
        return CropProcessor


if __name__ == "__main__":
    CropCli.main()
