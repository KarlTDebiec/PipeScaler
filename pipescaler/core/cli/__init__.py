#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Command line interfaces."""
from __future__ import annotations

from pipescaler.core.cli.processor_cli import ProcessorCli
from pipescaler.core.cli.utility_cli import UtilityCli

__all__: list[str] = [
    "ProcessorCli",
    "UtilityCli",
]
