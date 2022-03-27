#!/usr/bin/env python
#   pipescaler/scripts/processors/solid_color_command_line_tool.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Command-line interface for SolidColorProcessor."""
from __future__ import annotations

from argparse import ArgumentParser, _SubParsersAction
from typing import Type, Union

from pipescaler.core import Processor
from pipescaler.core.cl import ProcessorCommandLineTool
from pipescaler.processors import SolidColorProcessor


class SolidColorCommandLineTool(ProcessorCommandLineTool):
    """Command-line interface for SolidColorProcessor."""

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
            "--scale",
            default=2,
            type=cls.float_arg(min_value=0),
            help="scaling factor (default: %(default)s)",
        )

    @classmethod
    @property
    def processor(cls) -> Type[Processor]:
        """Type of processor wrapped by command-line tool."""
        return SolidColorProcessor


if __name__ == "__main__":
    SolidColorCommandLineTool.main()
