#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Command line interface for ScaledPairIdentifier."""
from __future__ import annotations

from argparse import ArgumentParser, _SubParsersAction
from typing import Type, Union

from pipescaler.core import Utility
from pipescaler.core.cli import UtilityCli
from pipescaler.utilities import ScaledPairIdentifier


class ScaledPairIdentifierCli(UtilityCli):
    """Command line interface for ScaledPairIdentifier."""

    @classmethod
    def add_arguments_to_argparser(
        cls,
        parser: Union[ArgumentParser, _SubParsersAction],
    ) -> None:
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: Nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        required = cls.get_required_arguments_group(parser)
        required.add_argument(
            "--input_directory",
            nargs="+",
            type=cls.input_path_arg(file_ok=True, directory_ok=True),
            help="input directories from which to read images",
        )
        required.add_argument(
            "--output_directory",
            required=False,
            type=cls.output_path_arg(file_ok=False, directory_ok=True),
            help="output directory to which to move scaled images",
        )
        required.add_argument(
            "--outfile",
            required=True,
            type=cls.output_path_arg(),
            help="output yaml file to which to write scaled file relationships",
        )

        optional = cls.get_optional_arguments_group(parser)
        optional.add_argument(
            "--infile",
            type=cls.input_path_arg(),
            help="input yaml file from which to read scaled file relationships",
        )
        optional.add_argument(
            "--threshold",
            default=0.9,
            type=cls.float_arg(min_value=0, max_value=1),
            help="structural similarity index measure (SSIM) threshold "
            "(default: %(default)f)",
        )

    @classmethod
    @property
    def utility(cls) -> Type[Utility]:
        """Type of utility wrapped by command line interface."""
        return ScaledPairIdentifier


if __name__ == "__main__":
    ScaledPairIdentifierCli.main()
