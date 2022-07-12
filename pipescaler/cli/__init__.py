#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Command line interfaces."""
from __future__ import annotations

from pipescaler.cli.pipescaler_cli import PipeScalerCli
from pipescaler.cli.processors_cli import ProcessorsCli
from pipescaler.cli.utilities_cli import UtilitiesCli

__all__: list[str] = [
    "PipeScalerCli",
    "ProcessorsCli",
    "UtilitiesCli",
]
