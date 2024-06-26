#!/usr/bin/env python
#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for SharpenProcessor."""
from __future__ import annotations

from typing import Type

from pipescaler.image.core.cli import ImageProcessorCli
from pipescaler.image.operators.processors import SharpenProcessor


class SharpenCli(ImageProcessorCli):
    """Command-line interface for SharpenProcessor."""

    @classmethod
    def processor(cls) -> Type[SharpenProcessor]:
        """Type of processor wrapped by command-line interface."""
        return SharpenProcessor


if __name__ == "__main__":
    SharpenCli.main()
