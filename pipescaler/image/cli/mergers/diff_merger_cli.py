#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for DiffMerger."""

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
from pipescaler.image.operators.mergers import DiffMerger

__all__ = ["DiffMergerCli"]


class DiffMergerCli(ImageMergerCli):
    """Command-line interface for DiffMerger."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        arg_groups = get_arg_groups_by_name(
            parser, "input arguments", "output arguments"
        )

        arg_groups["input arguments"].add_argument(
            "first_input_path",
            metavar="first_input_file",
            type=input_file_arg(),
            help="first input file",
        )
        arg_groups["input arguments"].add_argument(
            "second_input_path",
            metavar="second_input_file",
            type=input_file_arg(),
            help="second input file",
        )
        arg_groups["output arguments"].add_argument(
            "output_path",
            metavar="output_file",
            type=output_file_arg(),
            help="output file",
        )

    @classmethod
    def merger(cls) -> type[DiffMerger]:
        """Type of merger wrapped by command-line interface.

        Returns:
            merger implementation
        """
        return DiffMerger

    @classmethod
    def _main(
        cls, *, first_input_path: Path, second_input_path: Path, output_path: Path
    ):
        """Compare two input files and save their visual difference.

        Arguments:
            first_input_path: baseline image path
            second_input_path: comparison image path
            output_path: difference image path
        """
        merger = cls.merger()()
        with (
            Image.open(first_input_path) as first_img,
            Image.open(second_input_path) as second_img,
        ):
            output_img = merger(first_img, second_img)
            output_img.save(output_path)
            info(f"{cls}: '{output_path}' saved")


if __name__ == "__main__":
    DiffMergerCli.main()
