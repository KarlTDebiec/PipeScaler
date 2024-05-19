#!/usr/bin/env python
#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for HeightToNormalProcessor."""
from __future__ import annotations

from argparse import ArgumentParser
from typing import Type

from pipescaler.common.argument_parsing import float_arg, get_arg_groups_by_name
from pipescaler.image.core.cli import ImageProcessorCli
from pipescaler.image.operators.processors import HeightToNormalProcessor


class HeightToNormalCli(ImageProcessorCli):
    """Command-line interface for HeightToNormalProcessor."""

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
            "--sigma",
            default=None,
            type=float_arg(min_value=0),
            help="Gaussian smoothing to apply to image before calculating normal map "
            "(default: %(default)s)",
        )

    @classmethod
    def processor(cls) -> Type[HeightToNormalProcessor]:
        """Type of processor wrapped by command-line interface."""
        return HeightToNormalProcessor


if __name__ == "__main__":
    HeightToNormalCli.main()
