#!/usr/bin/env python
#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for PaletteMatchMerger."""
from __future__ import annotations

from argparse import ArgumentParser
from logging import info
from typing import Any, Type

from PIL import Image

from pipescaler.common.argument_parsing import input_file_arg, output_file_arg
from pipescaler.image.core import PaletteMatchMode
from pipescaler.image.core.cli import ImageMergerCli
from pipescaler.image.operators.mergers import PaletteMatchMerger


class PaletteMatchMergerCli(ImageMergerCli):
    """Command-line interface for PaletteMatchMerger."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser) -> None:
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: Nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        parser.add_argument(
            "reference_infile",
            type=input_file_arg(),
            help="reference input file",
        )
        parser.add_argument(
            "fit_infile",
            type=input_file_arg(),
            help="fit input file",
        )
        parser.add_argument(
            "outfile",
            type=output_file_arg(),
            help="output file",
        )
        parser.add_argument(
            "--local",
            action="store_const",
            const=PaletteMatchMode.LOCAL,
            default=PaletteMatchMode.BASIC,
            dest="palette_match_mode",
            help="Match only to local palette of surrounding pixels",
        )
        parser.add_argument(
            "--local_range",
            type=int,
            default=1,
            help="Range of surrounding pixels from which to draw best-fit color, if "
            "performing local matching (default: %(default)s)",
        )

    @classmethod
    def main_internal(cls, **kwargs: Any) -> None:
        """Execute with provided keyword arguments."""
        reference_infile = kwargs.pop("reference_infile")
        fit_infile = kwargs.pop("fit_infile")
        outfile = kwargs.pop("outfile")
        palette_match_mode = kwargs.pop("palette_match_mode")
        local_range = kwargs.pop("local_range")

        merger_cls = cls.merger()
        merger = merger_cls(
            palette_match_mode=palette_match_mode,
            local_range=local_range,
            **kwargs,
        )
        with (
            Image.open(reference_infile) as reference_image,
            Image.open(fit_infile) as fit_image,
        ):
            output_image = merger(reference_image, fit_image)
            output_image.save(outfile)
            info(f"{cls}: '{outfile}' saved")

    @classmethod
    def merger(cls) -> Type[PaletteMatchMerger]:
        """Type of merger wrapped by command-line interface."""
        return PaletteMatchMerger


if __name__ == "__main__":
    PaletteMatchMergerCli.main()
