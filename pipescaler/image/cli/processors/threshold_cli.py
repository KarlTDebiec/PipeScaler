#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Command line interface for ThresholdProcessor."""
from __future__ import annotations

from argparse import ArgumentParser
from typing import Type

from pipescaler.image.core.cli.processor_cli import ProcessorCli
from pipescaler.image.core.operators import ImageProcessor
from pipescaler.image.operators.processors import ThresholdProcessor


class ThresholdCli(ProcessorCli):
    """Command line interface for ThresholdProcessor."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser) -> None:
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: Nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        optional = cls.get_optional_arguments_group(parser)
        optional.add_argument(
            "--threshold",
            default=128,
            type=cls.int_arg(min_value=0, max_value=255),
            help="threshold differentiating black and white (0-255, default: "
            "%(default)s)",
        )
        optional.add_argument(
            "--denoise",
            action="store_true",
            help="Flip color of pixels bordered by less than 5 pixels of "
            "the same color",
        )

    @classmethod
    def processor(cls) -> Type[ImageProcessor]:
        """Type of processor wrapped by command line interface."""
        return ThresholdProcessor


if __name__ == "__main__":
    ThresholdCli.main()
