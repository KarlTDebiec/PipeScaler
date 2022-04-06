#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Command line interface for SharpenProcessor."""
from __future__ import annotations

from typing import Type

from pipescaler.core.cli import ProcessorCli
from pipescaler.core.stages import Processor
from pipescaler.processors import SharpenProcessor


class SharpenCli(ProcessorCli):
    """Command line interface for SharpenProcessor."""

    @classmethod
    @property
    def processor(cls) -> Type[Processor]:
        """Type of processor wrapped by command line interface."""
        return SharpenProcessor


if __name__ == "__main__":
    SharpenCli.main()
