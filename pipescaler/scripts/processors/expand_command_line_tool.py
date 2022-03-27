#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for ExpandProcessor."""
from __future__ import annotations

from argparse import ArgumentParser, _SubParsersAction
from typing import Type, Union

from pipescaler.core import Processor
from pipescaler.core.cl import ProcessorCommandLineTool
from pipescaler.processors import ExpandProcessor


class ExpandCommandLineTool(ProcessorCommandLineTool):
    """Command-line interface for ExpandProcessor."""

    @classmethod
    def add_arguments_to_argparser(
        cls,
        parser: Union[ArgumentParser, _SubParsersAction],
    ) -> None:
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: Nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        required = cls.get_required_arguments_group(parser)
        required.add_argument(
            "--pixels",
            default=(0, 0, 0, 0),
            metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"),
            nargs=4,
            type=cls.int_arg(0),
            help="number of pixels to add to left, top, right, and bottom "
            "(default: %(default)s)",
        )

    @classmethod
    @property
    def processor(cls) -> Type[Processor]:
        """Type of processor wrapped by command-line tool."""
        return ExpandProcessor


if __name__ == "__main__":
    ExpandCommandLineTool.main()
