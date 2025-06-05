#!/usr/bin/env python
#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for SolidColorProcessor."""
from __future__ import annotations

from argparse import ArgumentParser

from pipescaler.common.argument_parsing import float_arg, get_arg_groups_by_name
from pipescaler.image.core.cli import ImageProcessorCli
from pipescaler.image.operators.processors import SolidColorProcessor


class SolidColorCli(ImageProcessorCli):
    """Command-line interface for SolidColorProcessor."""

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

        arg_groups["required arguments"].add_argument(
            "--scale",
            default=1,
            type=float_arg(min_value=0),
            help="scaling factor (default: %(default)s)",
        )

    @classmethod
    def processor(cls) -> type[SolidColorProcessor]:
        """Type of processor wrapped by command-line interface."""
        return SolidColorProcessor


if __name__ == "__main__":
    SolidColorCli.main()
