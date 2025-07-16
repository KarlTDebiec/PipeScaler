#!/usr/bin/env python
#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for ThresholdProcessor."""

from __future__ import annotations

from argparse import ArgumentParser

from pipescaler.common.argument_parsing import get_arg_groups_by_name, int_arg
from pipescaler.image.core.cli import ImageProcessorCli
from pipescaler.image.operators.processors import ThresholdProcessor


class ThresholdCli(ImageProcessorCli):
    """Command-line interface for ThresholdProcessor."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser) -> None:
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: Nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        arg_groups = get_arg_groups_by_name(
            parser,
            "required arguments",
            optional_arguments_name="additional arguments",
        )

        arg_groups["additional arguments"].add_argument(
            "--threshold",
            default=128,
            type=int_arg(min_value=0, max_value=255),
            help="threshold differentiating black and white (0-255, default: "
            "%(default)s)",
        )
        arg_groups["additional arguments"].add_argument(
            "--denoise",
            action="store_true",
            help="Flip color of pixels bordered by less than 5 pixels of "
            "the same color",
        )

    @classmethod
    def processor(cls) -> type[ThresholdProcessor]:
        """Type of processor wrapped by command-line interface."""
        return ThresholdProcessor


if __name__ == "__main__":
    ThresholdCli.main()
