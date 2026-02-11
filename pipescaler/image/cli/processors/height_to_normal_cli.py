#!/usr/bin/env python
#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for HeightToNormalProcessor."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pipescaler.common.argument_parsing import float_arg, get_arg_groups_by_name
from pipescaler.image.core.cli import ImageProcessorCli
from pipescaler.image.operators.processors import HeightToNormalProcessor

if TYPE_CHECKING:
    from argparse import ArgumentParser


class HeightToNormalCli(ImageProcessorCli):
    """Command-line interface for HeightToNormalProcessor."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
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
            "--sigma",
            default=None,
            type=float_arg(min_value=0),
            help="Gaussian smoothing to apply to image before calculating normal map "
            "(default: %(default)s)",
        )

    @classmethod
    def processor(cls) -> type[HeightToNormalProcessor]:
        """Type of processor wrapped by command-line interface."""
        return HeightToNormalProcessor


if __name__ == "__main__":
    HeightToNormalCli.main()
