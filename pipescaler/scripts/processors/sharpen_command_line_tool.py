#!/usr/bin/env python
#   pipescaler/scripts/processors/sharpen_command_line_tool.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
from __future__ import annotations

from typing import Type

from pipescaler.core import Processor
from pipescaler.core.cl import ProcessorCommandLineTool
from pipescaler.processors import SharpenProcessor


class SharpenCommandLineTool(ProcessorCommandLineTool):
    @classmethod
    @property
    def processor(cls) -> Type[Processor]:
        """Type of processor wrapped by command-line tool."""
        return SharpenProcessor


if __name__ == "__main__":
    SharpenCommandLineTool.main()
