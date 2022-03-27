#!/usr/bin/env python
#   pipescaler/scripts/processors/height_to_normal_command_line_tool.py
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
from pipescaler.processors import HeightToNormalProcessor


class HeightToNormalCommandLineTool(ProcessorCommandLineTool):
    @classmethod
    def add_arguments_to_argparser(
        cls,
        parser: Union[ArgumentParser, _SubParsersAction],
    ) -> None:
        super().add_arguments_to_argparser(parser)

        optional = cls.get_optional_arguments_group(parser)
        parser.add_argument(
            "--sigma",
            default=None,
            type=cls.float_arg(min_value=0),
            help="Gaussian smoothing to apply to image before calculating normal map "
            "(default: %(default)s)",
        )

    @classmethod
    @property
    def processor(cls) -> type:
        return HeightToNormalProcessor


if __name__ == "__main__":
    HeightToNormalCommandLineTool.main()
