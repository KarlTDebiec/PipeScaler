#!/usr/bin/env python
#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for XbrzProcessor."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pipescaler.common.argument_parsing import get_arg_groups_by_name, int_arg
from pipescaler.image.core.cli import ImageProcessorCli
from pipescaler.image.operators.processors import XbrzProcessor

if TYPE_CHECKING:
    from argparse import ArgumentParser


class XbrzCli(ImageProcessorCli):
    """Command-line interface for XbrzProcessor."""

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
            default=2,
            type=int_arg(min_value=2, max_value=6),
            help="factor by which to scale image (2-6, default: %(default)s)",
        )

    @classmethod
    def processor(cls) -> type[XbrzProcessor]:
        """Type of processor wrapped by command-line interface."""
        return XbrzProcessor


if __name__ == "__main__":
    XbrzCli.main()
