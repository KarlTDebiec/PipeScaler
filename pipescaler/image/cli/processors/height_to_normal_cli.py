#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Command line interface for HeightToNormalProcessor."""
from __future__ import annotations

from argparse import ArgumentParser
from typing import Type

from pipescaler.image.core.cli.processor_cli import ProcessorCli
from pipescaler.image.core.operators import ImageProcessor
from pipescaler.image.operators.processors import HeightToNormalProcessor


class HeightToNormalCli(ProcessorCli):
    """Command line interface for HeightToNormalProcessor."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser) -> None:
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: Nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        optional = cls.get_optional_arguments_group(parser)
        optional.add_argument(
            "--sigma",
            default=None,
            type=cls.float_arg(min_value=0),
            help="Gaussian smoothing to apply to image before calculating normal map "
            "(default: %(default)s)",
        )

    @classmethod
    def processor(cls) -> Type[ImageProcessor]:
        """Type of processor wrapped by command line interface."""
        return HeightToNormalProcessor


if __name__ == "__main__":
    HeightToNormalCli.main()
