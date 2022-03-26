#!/usr/bin/env python
#   pipescaler/scripts/processors/crop_command_line_tool.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
from __future__ import annotations

from argparse import ArgumentParser, _SubParsersAction
from typing import Union

from pipescaler.core.cl import ProcessorCommandLineTool
from pipescaler.processors import CropProcessor


class CropCommandLineTool(ProcessorCommandLineTool):
    @classmethod
    def add_arguments_to_argparser(
        cls,
        parser: Union[ArgumentParser, _SubParsersAction],
    ) -> None:
        super().add_arguments_to_argparser(parser)

        required = cls.get_required_arguments_group(parser)
        required.add_argument(
            "--pixels",
            metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"),
            nargs=4,
            required=True,
            type=cls.int_arg(0),
            help="number of pixels to remove from each side",
        )

    @classmethod
    @property
    def processor(cls) -> type:
        return CropProcessor


if __name__ == "__main__":
    CropCommandLineTool.main()
