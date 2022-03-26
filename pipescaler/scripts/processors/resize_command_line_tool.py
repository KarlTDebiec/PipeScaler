#!/usr/bin/env python
#   pipescaler/scripts/processors/resize_command_line_tool.py
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
from pipescaler.processors import ResizeProcessor


class ResizeCommandLineTool(ProcessorCommandLineTool):
    @classmethod
    def add_arguments_to_argparser(
        cls,
        parser: Union[ArgumentParser, _SubParsersAction],
    ) -> None:
        super().add_arguments_to_argparser(parser)

        required = cls.get_required_arguments_group(parser)
        required.add_argument(
            "--scale",
            required=True,
            type=cls.float_arg(min_value=0),
            help="scaling factor",
        )

        optional = cls.get_optional_arguments_group(parser)
        optional.add_argument(
            "--resample",
            default="lanczos",
            type=cls.str_arg(options=cls.processor.resample_methods.keys()),
            help="Resampling method (default: %(default)s)",
        )

    @classmethod
    @property
    def processor(cls) -> type:
        return ResizeProcessor


if __name__ == "__main__":
    ResizeCommandLineTool.main()