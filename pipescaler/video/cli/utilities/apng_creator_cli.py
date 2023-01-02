#!/usr/bin/env python
#  Copyright 2020-2023 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for ApngCreator."""
from __future__ import annotations

from argparse import ArgumentParser
from typing import Type

from pipescaler.common import (
    get_optional_arguments_group,
    input_file_arg,
    int_arg,
    output_file_arg,
)
from pipescaler.core import Utility
from pipescaler.core.cli import UtilityCli
from pipescaler.video.runners.apngasm_runner import ApngasmRunner


class ApngCreatorCli(UtilityCli):
    """Command-line interface for ApngCreator."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser) -> None:
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: Nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        required = cls.get_required_arguments_group(parser)
        required.add_argument(
            "-i",
            "--infiles",
            nargs="+",
            required=True,
            type=input_file_arg(),
            help="input image files",
        )
        required.add_argument(
            "-o",
            "--outfile",
            default="out.png",
            required=True,
            type=output_file_arg(),
            help="output animated png",
        )

        optional = get_optional_arguments_group(parser)
        optional.add_argument(
            "--labels",
            nargs="+",
            type=str,
            help="labels with which to annotate images",
        )
        optional.add_argument(
            "--show_size",
            action="store_true",
            help="annotate each image with size",
        )
        optional.add_argument(
            "--duration",
            default=500,
            type=int_arg(min_value=1),
            help="duration for which to show each image (ms)",
        )

    @classmethod
    def utility(cls) -> Type[Utility]:
        """Type of utility wrapped by command-line interface."""
        return ApngasmRunner


if __name__ == "__main__":
    ApngCreatorCli.main()
