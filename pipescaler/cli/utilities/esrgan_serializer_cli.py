#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Command line interface for EsrganSerializer."""
from __future__ import annotations

from argparse import ArgumentParser, _SubParsersAction
from typing import Type, Union

from pipescaler.core import Utility
from pipescaler.core.cli import UtilityCli
from pipescaler.utilities.esrgan_serializer import EsrganSerializer


class EsrganSerializerCli(UtilityCli):
    """Command line interface for EsrganSerializer."""

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
            "infile", type=cls.input_path_arg(), help="input pth file"
        )
        required.add_argument(
            "outfile", type=cls.output_path_arg(), help="output pth file"
        )

    @classmethod
    @property
    def utility(cls) -> Type[Utility]:
        """Type of utility wrapped by command line interface."""
        return EsrganSerializer


if __name__ == "__main__":
    EsrganSerializerCli.main()
