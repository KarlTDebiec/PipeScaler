#!/usr/bin/env python
#  Copyright 2020-2023 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for WaifuSerializer."""
from __future__ import annotations

from argparse import ArgumentParser
from typing import Type

from pipescaler.core import Utility
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

        required = cls.get_required_arguments_group(parser)
        required.add_argument(
            "architecture",
            type=cls.str_arg(options=WaifuSerializer.architectures.keys()),
            help=f"model architecture {WaifuSerializer.architectures.keys()}",
        )
        required.add_argument(
            "infile", type=cls.input_file_arg(), help="input json file"
        )
        required.add_argument(
            "outfile", type=cls.output_file_arg(), help="output pth file"
        )

    @classmethod
    def main(cls) -> None:
        """Execute from command line."""
        parser = cls.argparser()
        kwargs = vars(parser.parse_args())
        kwargs.pop("verbosity")
        WaifuSerializer()(**kwargs)

    @classmethod
    def utility(cls) -> Type[Utility]:
        """Type of utility wrapped by command-line interface."""
        return WaifuSerializer


if __name__ == "__main__":
    WaifuSerializerCli.main()
