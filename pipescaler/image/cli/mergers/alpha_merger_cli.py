#!/usr/bin/env python
#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for AlphaMerger."""

from __future__ import annotations

from argparse import ArgumentParser
from logging import info
from typing import Any

from PIL import Image

from pipescaler.common.argument_parsing import input_file_arg, output_file_arg
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
            "color_input_file",
            type=input_file_arg(),
            help="color input file",
        )
        parser.add_argument(
            "alpha_input_file",
            type=input_file_arg(),
            help="alpha input file",
        )
        parser.add_argument(
            "output_file",
            type=output_file_arg(),
            help="output file",
        )

    @classmethod
    def _main(cls, **kwargs: Any) -> None:
        """Execute with provided keyword arguments."""
        color_input_path = kwargs.pop("color_input_file")
        alpha_input_path = kwargs.pop("alpha_input_file")
        output_path = kwargs.pop("output_file")
        merger_cls = cls.merger()
        merger = merger_cls(**kwargs)
        with (
            Image.open(color_input_path) as color_img,
            Image.open(alpha_input_path) as alpha_img,
        ):
            output_img = merger(color_img, alpha_img)
            output_img.save(output_path)
            info(f"{cls}: '{output_path}' saved")

    @classmethod
    def merger(cls) -> type[AlphaMerger]:
        """Type of merger wrapped by command-line interface."""
        return AlphaMerger


if __name__ == "__main__":
    AlphaMergerCli.main()
