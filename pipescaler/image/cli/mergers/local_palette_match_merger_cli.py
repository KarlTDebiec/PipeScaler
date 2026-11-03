#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for LocalPaletteMatchMerger."""

from __future__ import annotations

from argparse import ArgumentParser
from logging import info
from pathlib import Path

from PIL import Image

from pipescaler.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
    int_arg,
    output_file_arg,
)
from pipescaler.image.core.cli import ImageMergerCli
from pipescaler.image.operators.mergers import LocalPaletteMatchMerger

__all__ = ["LocalPaletteMatchMergerCli"]


class LocalPaletteMatchMergerCli(ImageMergerCli):
    """Command-line interface for LocalPaletteMatchMerger."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        arg_groups = get_arg_groups_by_name(
            parser, "input arguments", "operation arguments", "output arguments"
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
            help="target input file; width and height must be the same integer "
            "multiple of the reference, at least 2",
        )

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "output_path",
            metavar="output_file",
            type=output_file_arg(),
            help="output file",
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--local-range",
            type=int_arg(min_value=1),
            default=1,
            help="reference-pixel neighborhood radius (default: %(default)s)",
        )

    @classmethod
    def merger(cls) -> type[LocalPaletteMatchMerger]:
        """Type of merger wrapped by command-line interface.

        Returns:
            merger implementation
        """
        return LocalPaletteMatchMerger

    @classmethod
    def _main(
        cls,
        *,
        reference_input_path: Path,
        fit_input_path: Path,
        output_path: Path,
        local_range: int,
    ):
        """Match target colors to the reference palette.

        Arguments:
            reference_input_path: reference image path
            fit_input_path: target image path
            output_path: matched image path
            local_range: neighborhood radius in reference pixels
        """
        merger = cls.merger()(local_range=local_range)
        with (
            Image.open(reference_input_path) as reference_img,
            Image.open(fit_input_path) as fit_img,
        ):
            output_img = merger(reference_img, fit_img)
            output_img.save(output_path)
            info(f"{cls}: '{output_path}' saved")


if __name__ == "__main__":
    LocalPaletteMatchMergerCli.main()
