#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Command line interface for SharpenProcessor."""
from __future__ import annotations

from typing import Type

from pipescaler.core.cli import ProcessorCli
from pipescaler.core.image import Processor
from pipescaler.image.processors import SharpenProcessor


class SharpenCli(ProcessorCli):
    """Command line interface for SharpenProcessor."""

    @classmethod
    def processor(cls) -> Type[Processor]:
        """Type of processor wrapped by command line interface."""
        return SharpenProcessor


if __name__ == "__main__":
    SharpenCli.main()
