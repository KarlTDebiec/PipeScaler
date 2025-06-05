#!/usr/bin/env python
#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for AlphaSplitter."""
from __future__ import annotations

from argparse import ArgumentParser
from logging import info
from typing import Any, Type

from PIL import Image

from pipescaler.common.argument_parsing import output_file_arg
from pipescaler.image.core.cli import ImageSplitterCli
from pipescaler.image.core.operators import ImageSplitter
from pipescaler.image.operators.splitters import AlphaSplitter


class AlphaSplitterCli(ImageSplitterCli):
    """Command-line interface for AlphaSplitter."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser) -> None:
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: Nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        parser.add_argument(
            "color_outfile",
            type=output_file_arg(),
            help="color output file",
        )
        parser.add_argument(
            "alpha_outfile",
            type=output_file_arg(),
            help="alpha output file",
        )

    @classmethod
    def _main(cls, **kwargs: Any) -> None:
        """Execute with provided keyword arguments."""
        infile = kwargs.pop("infile")
        color_outfile = kwargs.pop("color_outfile")
        alpha_outfile = kwargs.pop("alpha_outfile")
        splitter_cls = cls.splitter()
        splitter = splitter_cls(**kwargs)
        with Image.open(infile) as input_image:
            color_image, alpha_image = splitter(input_image)
            color_image.save(color_outfile)
            info(f"{cls}: '{color_outfile}' saved")
            alpha_image.save(alpha_outfile)
            info(f"{cls}: '{alpha_outfile}' saved")

    @classmethod
    def splitter(cls) -> Type[ImageSplitter]:
        """Type of splitter wrapped by command-line interface."""
        return AlphaSplitter


if __name__ == "__main__":
    AlphaSplitterCli.main()
