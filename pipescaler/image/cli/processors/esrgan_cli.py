#!/usr/bin/env python
#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for EsrganProcessor."""
from __future__ import annotations

from argparse import ArgumentParser

from pipescaler.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
    str_arg,
)
from pipescaler.image.core.cli import ImageProcessorCli
from pipescaler.image.operators.processors import EsrganProcessor


class EsrganCli(ImageProcessorCli):
    """Command-line interface for EsrganProcessor."""

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
            "--model",
            dest="model_infile",
            required=True,
            type=input_file_arg(),
            help="model input file",
        )

        arg_groups["additional arguments"].add_argument(
            "--device",
            default="cuda",
            type=str_arg(options=["cpu", "cuda"]),
            help="device (default: %(default)s)",
        )

    @classmethod
    def processor(cls) -> type[EsrganProcessor]:
        """Type of processor wrapped by command-line interface."""
        return EsrganProcessor


if __name__ == "__main__":
    EsrganCli.main()
