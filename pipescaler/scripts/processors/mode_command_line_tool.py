#!/usr/bin/env python
#   pipescaler/scripts/processors/mode_command_line_tool.py
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
from pipescaler.processors import ModeProcessor


class ModeCommandLineTool(ProcessorCommandLineTool):
    @classmethod
    def add_arguments_to_argparser(
        cls,
        parser: Union[ArgumentParser, _SubParsersAction],
    ) -> None:
        super().add_arguments_to_argparser(parser)

        required = cls.get_required_arguments_group(parser)
        required.add_argument(
            "--mode",
            required=True,
            type=cls.str_arg(options=cls.processor.supported_input_modes),
            help=f"image mode ({ModeProcessor.supported_input_modes})",
        )

        optional = cls.get_optional_arguments_group(parser)
        optional.add_argument(
            "--background_color",
            default="#000000",
            type=str,
            help="background color of output image; only relevant if input image is "
            "RGBA or LA (default: %(default)s)",
        )

    @classmethod
    @property
    def processor(cls) -> type:
        return ModeProcessor


if __name__ == "__main__":
    ModeCommandLineTool.main()
