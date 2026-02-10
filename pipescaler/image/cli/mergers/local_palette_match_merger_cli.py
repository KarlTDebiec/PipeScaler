#!/usr/bin/env python
#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for LocalPaletteMatchMerger."""

from __future__ import annotations

from argparse import ArgumentParser
from logging import info
from typing import Any

from PIL import Image

from pipescaler.common.argument_parsing import input_file_arg, output_file_arg
from pipescaler.image.core.cli import ImageMergerCli
from pipescaler.image.operators.mergers import LocalPaletteMatchMerger


class LocalPaletteMatchMergerCli(ImageMergerCli):
    """Command-line interface for LocalPaletteMatchMerger."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: Nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        parser.add_argument(
            "reference_input_file",
            type=input_file_arg(),
            help="reference input file",
        )
        parser.add_argument(
            "fit_input_file",
            type=input_file_arg(),
            help="fit input file",
        )
        parser.add_argument(
            "output_file",
            type=output_file_arg(),
            help="output file",
        )
        parser.add_argument(
            "--local_range",
            type=int,
            default=1,
            help="Range of surrounding pixels from which to draw best-fit color "
            "(default: %(default)s)",
        )

    @classmethod
    def _main(cls, **kwargs: Any):
        """Execute with provided keyword arguments."""
        reference_input_path = kwargs.pop("reference_input_file")
        fit_input_path = kwargs.pop("fit_input_file")
        output_path = kwargs.pop("output_file")
        local_range = kwargs.pop("local_range")

        merger_cls = cls.merger()
        merger = merger_cls(
            local_range=local_range,
            **kwargs,
        )
        with (
            Image.open(reference_input_path) as reference_img,
            Image.open(fit_input_path) as fit_img,
        ):
            output_img = merger(reference_img, fit_img)
            output_img.save(output_path)
            info(f"{cls}: '{output_path}' saved")

    @classmethod
    def merger(cls) -> type[LocalPaletteMatchMerger]:
        """Type of merger wrapped by command-line interface."""
        return LocalPaletteMatchMerger


if __name__ == "__main__":
    LocalPaletteMatchMergerCli.main()
