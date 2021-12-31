#!/usr/bin/env python
#   pipescaler/processors/gigapixel_ai_processor.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
from __future__ import annotations

from typing import Any

from pipescaler.core import Processor


class GigapixelAiProcessor(Processor):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        # Store configuration

    def __call__(self, infile: str, outfile: str) -> None:
        pass


if __name__ == "__main__":
    GigapixelAiProcessor.main()
