#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Command line interface for WaifuProcessor."""
from __future__ import annotations

from argparse import ArgumentParser, _SubParsersAction
from typing import Type, Union

from pipescaler.core.cli import ProcessorCli
from pipescaler.core.stages import Processor
from pipescaler.processors import WaifuProcessor


class WaifuCli(ProcessorCli):
    """Command line interface for WaifuProcessor."""

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
            "--model",
            dest="model_infile",
            required=True,
            type=cls.input_path_arg(),
            help="model input file",
        )

        optional = cls.get_optional_arguments_group(parser)
        optional.add_argument(
            "--device",
            default="cuda",
            type=cls.str_arg(options=["cpu", "cuda"]),
            help="device (default: %(default)s)",
        )

    @classmethod
    @property
    def processor(cls) -> Type[Processor]:
        """Type of processor wrapped by command line interface."""
        return WaifuProcessor


if __name__ == "__main__":
    WaifuCli.main()
