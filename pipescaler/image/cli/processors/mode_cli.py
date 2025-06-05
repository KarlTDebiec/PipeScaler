#!/usr/bin/env python
#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for ModeProcessor."""
from __future__ import annotations

from argparse import ArgumentParser

from pipescaler.common.argument_parsing import get_arg_groups_by_name, str_arg
from pipescaler.image.core.cli import ImageProcessorCli
from pipescaler.image.operators.processors import ModeProcessor


class ModeCli(ImageProcessorCli):
    """Command-line interface for ModeProcessor."""

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
            "--mode",
            required=True,
            type=str_arg(options=ModeProcessor.inputs()["input"]),
            help=f"image mode ({ModeProcessor.inputs()['input']})",
        )

        arg_groups["additional arguments"].add_argument(
            "--background_color",
            default="#000000",
            type=str,
            help="background color of output image; only relevant if input image is "
            "RGBA or LA (default: %(default)s)",
        )
        arg_groups["additional arguments"].add_argument(
            "--threshold",
            default=128,
            type=int,
            help="threshold for binary conversion; only relevant if mode=1) "
            "(default: %(default)s)",
        )

    @classmethod
    def processor(cls) -> type[ModeProcessor]:
        """Type of processor wrapped by command-line interface."""
        return ModeProcessor


if __name__ == "__main__":
    ModeCli.main()
