#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for AlphaMerger."""

from __future__ import annotations

from argparse import ArgumentParser
from logging import info
from pathlib import Path

from PIL import Image

from pipescaler.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
    output_file_arg,
)
from pipescaler.image.core.cli import ImageMergerCli
from pipescaler.image.operators.mergers import AlphaMerger

__all__ = ["AlphaMergerCli"]


class AlphaMergerCli(ImageMergerCli):
    """Command-line interface for AlphaMerger."""

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

        arg_groups["input arguments"].add_argument(
            "color_input_path",
            metavar="color_input_file",
            type=input_file_arg(),
            help="color input file",
        )
        arg_groups["input arguments"].add_argument(
            "alpha_input_path",
            metavar="alpha_input_file",
            type=input_file_arg(),
            help="alpha input file",
        )
        arg_groups["output arguments"].add_argument(
            "output_path",
            metavar="output_file",
            type=output_file_arg(),
            help="output file",
        )

    @classmethod
    def merger(cls) -> type[AlphaMerger]:
        """Type of merger wrapped by command-line interface.

        Returns:
            image merger class invoked by this command
        """
        return AlphaMerger

    @classmethod
    def _main(
        cls, *, color_input_path: Path, alpha_input_path: Path, output_path: Path
    ):
        """Execute with parsed image paths and operation settings.

        Arguments:
            color_input_path: color input path
            alpha_input_path: alpha input path
            output_path: output path
        """
        merger_cls = cls.merger()
        merger = merger_cls()
        with (
            Image.open(color_input_path) as color_img,
            Image.open(alpha_input_path) as alpha_img,
        ):
            output_img = merger(color_img, alpha_img)
            output_img.save(output_path)
            info(f"{cls}: '{output_path}' saved")


if __name__ == "__main__":
    AlphaMergerCli.main()
