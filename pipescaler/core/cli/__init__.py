#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Abstract base classes for command line interfaces."""
from __future__ import annotations

from pipescaler.core.cli.configurable_cli import ConfigurableCli
from pipescaler.core.cli.processor_cli import ProcessorCli
from pipescaler.core.cli.utility_cli import UtilityCli

__all__: list[str] = [
    "ConfigurableCli",
    "ProcessorCli",
    "UtilityCli",
]
