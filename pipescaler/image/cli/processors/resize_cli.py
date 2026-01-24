#!/usr/bin/env python
#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for ResizeProcessor."""

from __future__ import annotations

from argparse import ArgumentParser

from pipescaler.common.argument_parsing import (
    float_arg,
    get_arg_groups_by_name,
    str_arg,
)
from pipescaler.image.core.cli import ImageProcessorCli
from pipescaler.image.operators.processors import ResizeProcessor


class ResizeCli(ImageProcessorCli):
    """Command-line interface for ResizeProcessor."""

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

        arg_groups["required arguments"].add_argument(
            "--scale",
            required=True,
            type=float_arg(min_value=0),
            help="scaling factor",
        )

        arg_groups["additional arguments"].add_argument(
            "--resample",
            default="lanczos",
            type=str_arg(options=ResizeProcessor.resample_methods.keys()),
            help="Resampling method (default: %(default)s)",
        )

    @classmethod
    def processor(cls) -> type[ResizeProcessor]:
        """Type of processor wrapped by command-line interface."""
        return ResizeProcessor


if __name__ == "__main__":
    ResizeCli.main()
