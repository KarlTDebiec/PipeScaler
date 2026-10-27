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
from pipescaler.image.core import PaletteMatchMode
from pipescaler.image.core.cli import ImageMergerCli
from pipescaler.image.operators.mergers import PaletteMatchMerger

__all__ = ["PaletteMatchMergerCli"]


class PaletteMatchMergerCli(ImageMergerCli):
    """Command-line interface for PaletteMatchMerger."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: Nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        arg_groups = get_arg_groups_by_name(
            parser, "input arguments", "operation arguments", "output arguments"
        )

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
            help="fit input file",
        )
        arg_groups["output arguments"].add_argument(
            "output_path",
            metavar="output_file",
            type=output_file_arg(),
            help="output file",
        )
        arg_groups["operation arguments"].add_argument(
            "--local",
            action="store_const",
            const=PaletteMatchMode.LOCAL,
            default=PaletteMatchMode.BASIC,
            dest="palette_match_mode",
            help="Match only to local palette of surrounding pixels; target width and "
            "height must be the same integer multiple of the reference, at least 2",
        )
        arg_groups["operation arguments"].add_argument(
            "--local-range",
            type=int,
            default=1,
            help="Range of surrounding reference pixels from which to draw best-fit "
            "color, if performing local matching (default: %(default)s)",
        )

    @classmethod
    def merger(cls) -> type[PaletteMatchMerger]:
        """Type of merger wrapped by command-line interface.

        Returns:
            image merger class invoked by this command
        """
        return PaletteMatchMerger

    @classmethod
    def _main(
        cls,
        *,
        reference_input_path: Path,
        fit_input_path: Path,
        output_path: Path,
        palette_match_mode: PaletteMatchMode,
        local_range: int,
    ):
        """Execute with parsed image paths and operation settings.

        Arguments:
            reference_input_path: reference input path
            fit_input_path: fit input path
            output_path: output path
            palette_match_mode: palette matching strategy
            local_range: radius of local reference pixels
        """
        merger_cls = cls.merger()
        merger = merger_cls(
            palette_match_mode=palette_match_mode,
            local_range=local_range,
        )
        with (
            Image.open(reference_input_path) as reference_img,
            Image.open(fit_input_path) as fit_img,
        ):
            output_img = merger(reference_img, fit_img)
            output_img.save(output_path)
            info(f"{cls}: '{output_path}' saved")


if __name__ == "__main__":
    PaletteMatchMergerCli.main()
