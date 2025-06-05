#!/usr/bin/env python
#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for EsrganSerializer."""
from __future__ import annotations

from argparse import ArgumentParser

from pipescaler.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
    output_file_arg,
)
from pipescaler.core.cli import UtilityCli
from pipescaler.image.utilities.esrgan_serializer import EsrganSerializer


class EsrganSerializerCli(UtilityCli):
    """Command-line interface for EsrganSerializer."""

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
            "infile",
            type=input_file_arg(),
            help="input pth file",
        )
        arg_groups["required arguments"].add_argument(
            "outfile",
            type=output_file_arg(),
            help="output pth file",
        )

    @classmethod
    def utility(cls) -> type[EsrganSerializer]:
        """Type of utility wrapped by command-line interface."""
        return EsrganSerializer


if __name__ == "__main__":
    EsrganSerializerCli.main()
