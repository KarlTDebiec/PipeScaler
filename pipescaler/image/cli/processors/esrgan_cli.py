#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Command line interface for EsrganProcessor."""
from __future__ import annotations

from argparse import ArgumentParser
from typing import Type

from pipescaler.image.core.cli.processor_cli import ProcessorCli
from pipescaler.image.core.operators import ImageProcessor
from pipescaler.image.operators.processors import EsrganProcessor


class EsrganCli(ProcessorCli):
    """Command line interface for EsrganProcessor."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser) -> None:
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
            type=cls.input_file_arg(),
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
    def processor(cls) -> Type[ImageProcessor]:
        """Type of processor wrapped by command line interface."""
        return EsrganProcessor


if __name__ == "__main__":
    EsrganCli.main()
