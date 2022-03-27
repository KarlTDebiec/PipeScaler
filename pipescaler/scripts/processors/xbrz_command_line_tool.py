#!/usr/bin/env python
#   pipescaler/scripts/processors/xbrz_command_line_tool.py
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
from pipescaler.processors import XbrzProcessor


class XbrzCommandLineTool(ProcessorCommandLineTool):
    @classmethod
    def add_arguments_to_argparser(
        cls,
        parser: Union[ArgumentParser, _SubParsersAction],
    ) -> None:
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
    def processor(cls) -> type:
        return XbrzProcessor


if __name__ == "__main__":
    XbrzCommandLineTool.main()
