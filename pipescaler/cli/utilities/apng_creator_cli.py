#!/usr/bin/env python
#  Copyright (C) 2020-2022. Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Command line interface for ApngCreator."""
from __future__ import annotations

from argparse import ArgumentParser, _SubParsersAction
from typing import Type, Union

from pipescaler.core import Utility
from pipescaler.core.cli import UtilityCli
from pipescaler.utilities.apng_creator import ApngCreator


class ApngCreatorCli(UtilityCli):
    """Command line interface for ApngCreator."""

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
            "-i",
            "--infiles",
            nargs="+",
            required=True,
            type=cls.input_file_arg(),
            help="input image files",
        )
        required.add_argument(
            "-o",
            "--outfile",
            default="out.png",
            required=True,
            type=cls.output_file_arg(),
            help="output animated png",
        )

        optional = cls.get_optional_arguments_group(parser)
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
            type=cls.int_arg(min_value=1),
            help="duration for which to show each image (ms)",
        )

    @classmethod
    @property
    def utility(cls) -> Type[Utility]:
        """Type of utility wrapped by command line interface."""
        return ApngCreator


if __name__ == "__main__":
    ApngCreatorCli.main()
