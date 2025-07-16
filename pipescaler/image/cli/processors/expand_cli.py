#!/usr/bin/env python
#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for ExpandProcessor."""

from __future__ import annotations

from argparse import ArgumentParser

from pipescaler.common.argument_parsing import get_arg_groups_by_name, int_arg
from pipescaler.image.core.cli import ImageProcessorCli
from pipescaler.image.operators.processors import ExpandProcessor


class ExpandCli(ImageProcessorCli):
    """Command-line interface for ExpandProcessor."""

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
            "--pixels",
            default=(0, 0, 0, 0),
            metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"),
            nargs=4,
            type=int_arg(min_value=1),
            help="number of pixels to add to left, top, right, and bottom "
            "(default: %(default)s)",
        )

    @classmethod
    def processor(cls) -> type[ExpandProcessor]:
        """Type of processor wrapped by command-line interface."""
        return ExpandProcessor


if __name__ == "__main__":
    ExpandCli.main()
