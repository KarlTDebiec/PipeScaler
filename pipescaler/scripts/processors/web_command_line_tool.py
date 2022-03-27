#!/usr/bin/env python
#   pipescaler/scripts/processors/web_command_line_tool.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
from __future__ import annotations

from argparse import ArgumentParser, _SubParsersAction
from typing import Union

from pipescaler.core import Processor
from pipescaler.core.cl import ProcessorCommandLineTool
from pipescaler.processors import WebProcessor


class WebCommandLineTool(ProcessorCommandLineTool):
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
        parser.add_argument("--url", type=str, help="URL to which to POST image")

    @classmethod
    @property
    def processor(cls) -> type[Processor]:
        """Type of processor wrapped by command-line tool."""
        return WebProcessor


if __name__ == "__main__":
    WebCommandLineTool.main()
