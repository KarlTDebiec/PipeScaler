#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for AlphaSplitter."""

from __future__ import annotations

from argparse import ArgumentParser
from logging import info
from pathlib import Path

from PIL import Image

from pipescaler.common.argument_parsing import get_arg_groups_by_name, output_file_arg
from pipescaler.image.core.cli import ImageSplitterCli
from pipescaler.image.core.operators import ImageSplitter
from pipescaler.image.operators.splitters import AlphaSplitter

__all__ = ["AlphaSplitterCli"]


class AlphaSplitterCli(ImageSplitterCli):
    """Command-line interface for AlphaSplitter."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: Nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        arg_groups = get_arg_groups_by_name(
            parser, "input arguments", "output arguments"
        )

        arg_groups["output arguments"].add_argument(
            "color_output_path",
            metavar="color_output_file",
            type=output_file_arg(),
            help="color output file",
        )
        arg_groups["output arguments"].add_argument(
            "alpha_output_path",
            metavar="alpha_output_file",
            type=output_file_arg(),
            help="alpha output file",
        )

    @classmethod
    def splitter(cls) -> type[ImageSplitter]:
        """Type of splitter wrapped by command-line interface.

        Returns:
            image splitter class invoked by this command
        """
        return AlphaSplitter

    @classmethod
    def _main(
        cls, *, input_path: Path, color_output_path: Path, alpha_output_path: Path
    ):
        """Execute with parsed image paths and operation settings.

        Arguments:
            input_path: input path
            color_output_path: color output path
            alpha_output_path: alpha output path
        """
        splitter_cls = cls.splitter()
        splitter = splitter_cls()
        with Image.open(input_path) as input_img:
            color_img, alpha_img = splitter(input_img)
            color_img.save(color_output_path)
            info(f"{cls}: '{color_output_path}' saved")
            alpha_img.save(alpha_output_path)
            info(f"{cls}: '{alpha_output_path}' saved")


if __name__ == "__main__":
    AlphaSplitterCli.main()
