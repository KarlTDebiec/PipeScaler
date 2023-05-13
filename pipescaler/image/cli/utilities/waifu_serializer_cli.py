#!/usr/bin/env python
#  Copyright 2020-2023 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for WaifuSerializer."""
from __future__ import annotations

from argparse import ArgumentParser
from typing import Any, Type

from pipescaler.common import (
    get_arg_groups_by_name,
    input_file_arg,
    output_file_arg,
    str_arg,
)
from pipescaler.core.cli import UtilityCli
from pipescaler.image.utilities import WaifuSerializer


class WaifuSerializerCli(UtilityCli):
    """Command-line interface for WaifuSerializer."""

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
            "architecture",
            type=str_arg(options=WaifuSerializer.architectures.keys()),
            help=f"model architecture {WaifuSerializer.architectures.keys()}",
        )
        arg_groups["required arguments"].add_argument(
            "infile",
            type=input_file_arg(),
            help="input json file",
        )
        arg_groups["required arguments"].add_argument(
            "outfile",
            type=output_file_arg(),
            help="output pth file",
        )

    @classmethod
    def main_internal(cls, **kwargs: Any) -> None:
        """Execute with provided keyword arguments."""
        utility_cls = cls.utility()
        utility_cls.run(**kwargs)

    @classmethod
    def utility(cls) -> Type[WaifuSerializer]:
        """Type of utility wrapped by command-line interface."""
        return WaifuSerializer


if __name__ == "__main__":
    WaifuSerializerCli.main()
