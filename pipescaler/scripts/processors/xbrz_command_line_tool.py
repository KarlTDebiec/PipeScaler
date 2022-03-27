#!/usr/bin/env python
#   pipescaler/scripts/processors/xbrz_command_line_tool.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for XbrzProcessor."""
from __future__ import annotations

from argparse import ArgumentParser, _SubParsersAction
from typing import Type, Union

from pipescaler.core import Processor
from pipescaler.core.cl import ProcessorCommandLineTool
from pipescaler.processors import XbrzProcessor


class XbrzCommandLineTool(ProcessorCommandLineTool):
    """Command-line interface for XbrzProcessor."""

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
            type=cls.int_arg(min_value=2, max_value=6),
            help="factor by which to scale image (2-6, default: %(default)s)",
        )

    @classmethod
    @property
    def processor(cls) -> Type[Processor]:
        """Type of processor wrapped by command-line tool."""
        return XbrzProcessor


if __name__ == "__main__":
    XbrzCommandLineTool.main()
