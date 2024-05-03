#!/usr/bin/env python
#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for AlphaMerger."""
from __future__ import annotations

from argparse import ArgumentParser
from logging import info
from typing import Any, Type

from PIL import Image

from pipescaler.common import input_file_arg, output_file_arg
from pipescaler.image.core.cli import ImageMergerCli
from pipescaler.image.operators.mergers import AlphaMerger


class AlphaMergerCli(ImageMergerCli):
    """Command-line interface for AlphaMerger."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser) -> None:
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: Nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        parser.add_argument(
            "color_infile",
            type=input_file_arg(),
            help="color input file",
        )
        parser.add_argument(
            "alpha_infile",
            type=input_file_arg(),
            help="alpha input file",
        )
        parser.add_argument(
            "outfile",
            type=output_file_arg(),
            help="output file",
        )

    @classmethod
    def main_internal(cls, **kwargs: Any) -> None:
        """Execute with provided keyword arguments."""
        color_infile = kwargs.pop("color_infile")
        alpha_infile = kwargs.pop("alpha_infile")
        outfile = kwargs.pop("outfile")
        merger_cls = cls.merger()
        merger = merger_cls(**kwargs)
        with (
            Image.open(color_infile) as color_image,
            Image.open(alpha_infile) as alpha_image,
        ):
            output_image = merger(color_image, alpha_image)
            output_image.save(outfile)
            info(f"{cls}: '{outfile}' saved")

    @classmethod
    def merger(cls) -> Type[AlphaMerger]:
        """Type of merger wrapped by command-line interface."""
        return AlphaMerger


if __name__ == "__main__":
    AlphaMergerCli.main()
