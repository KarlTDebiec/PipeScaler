#!/usr/bin/env python
#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for AlphaSplitter."""

from __future__ import annotations

from argparse import ArgumentParser
from logging import info
from typing import Any

from PIL import Image

from pipescaler.common.argument_parsing import output_file_arg
from pipescaler.image.core.cli import ImageSplitterCli
from pipescaler.image.core.operators import ImageSplitter
from pipescaler.image.operators.splitters import AlphaSplitter


class AlphaSplitterCli(ImageSplitterCli):
    """Command-line interface for AlphaSplitter."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: Nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        parser.add_argument(
            "color_output_file",
            type=output_file_arg(),
            help="color output file",
        )
        parser.add_argument(
            "alpha_output_file",
            type=output_file_arg(),
            help="alpha output file",
        )

    @classmethod
    def _main(cls, **kwargs: Any):
        """Execute with provided keyword arguments."""
        input_path = kwargs.pop("input_file")
        color_output_path = kwargs.pop("color_output_file")
        alpha_output_path = kwargs.pop("alpha_output_file")
        splitter_cls = cls.splitter()
        splitter = splitter_cls(**kwargs)
        with Image.open(input_path) as input_img:
            color_img, alpha_img = splitter(input_img)
            color_img.save(color_output_path)
            info(f"{cls}: '{color_output_path}' saved")
            alpha_img.save(alpha_output_path)
            info(f"{cls}: '{alpha_output_path}' saved")

    @classmethod
    def splitter(cls) -> type[ImageSplitter]:
        """Type of splitter wrapped by command-line interface."""
        return AlphaSplitter


if __name__ == "__main__":
    AlphaSplitterCli.main()
