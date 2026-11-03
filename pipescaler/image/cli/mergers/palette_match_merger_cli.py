#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for PaletteMatchMerger."""

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
from pipescaler.image.operators.mergers import PaletteMatchMerger

__all__ = ["PaletteMatchMergerCli"]


class PaletteMatchMergerCli(ImageMergerCli):
    """Command-line interface for PaletteMatchMerger."""

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

        # Input arguments
        arg_groups["input arguments"].add_argument(
            "reference_input_path",
            metavar="reference_input_file",
            type=input_file_arg(),
            help="reference input file",
        )
        arg_groups["input arguments"].add_argument(
            "fit_input_path",
            metavar="fit_input_file",
            type=input_file_arg(),
            help="target input file",
        )

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "output_path",
            metavar="output_file",
            type=output_file_arg(),
            help="output file",
        )

    @classmethod
    def merger(cls) -> type[PaletteMatchMerger]:
        """Type of merger wrapped by command-line interface.

        Returns:
            merger implementation
        """
        return PaletteMatchMerger

    @classmethod
    def _main(
        cls, *, reference_input_path: Path, fit_input_path: Path, output_path: Path
    ):
        """Match target colors to the reference palette.

        Arguments:
            reference_input_path: reference image path
            fit_input_path: target image path
            output_path: matched image path
        """
        merger = cls.merger()()
        with (
            Image.open(reference_input_path) as reference_img,
            Image.open(fit_input_path) as fit_img,
        ):
            output_img = merger(reference_img, fit_img)
            output_img.save(output_path)
            info(f"{cls}: '{output_path}' saved")


if __name__ == "__main__":
    PaletteMatchMergerCli.main()
