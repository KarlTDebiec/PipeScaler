#!/usr/bin/env python
#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for DiffMerger."""

from __future__ import annotations

from logging import info
from typing import TYPE_CHECKING, Any

from PIL import Image

from pipescaler.common.argument_parsing import input_file_arg, output_file_arg
from pipescaler.image.core.cli import ImageMergerCli
from pipescaler.image.operators.mergers import DiffMerger

if TYPE_CHECKING:
    from argparse import ArgumentParser


class DiffMergerCli(ImageMergerCli):
    """Command-line interface for DiffMerger."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: Nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        parser.add_argument(
            "first_input_file",
            type=input_file_arg(),
            help="first input file",
        )
        parser.add_argument(
            "second_input_file",
            type=input_file_arg(),
            help="second input file",
        )
        parser.add_argument(
            "output_file",
            type=output_file_arg(),
            help="output file",
        )

    @classmethod
    def _main(cls, **kwargs: Any):
        """Execute with provided keyword arguments."""
        first_input_path = kwargs.pop("first_input_file")
        second_input_path = kwargs.pop("second_input_file")
        output_path = kwargs.pop("output_file")
        merger_cls = cls.merger()
        merger = merger_cls(**kwargs)
        with (
            Image.open(first_input_path) as first_img,
            Image.open(second_input_path) as second_img,
        ):
            output_img = merger(first_img, second_img)
            output_img.save(output_path)
            info(f"{cls}: '{output_path}' saved")

    @classmethod
    def merger(cls) -> type[DiffMerger]:
        """Type of merger wrapped by command-line interface."""
        return DiffMerger


if __name__ == "__main__":
    DiffMergerCli.main()
