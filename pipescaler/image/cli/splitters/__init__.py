#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PipeScaler image splitter command-line interfaces package.

This module may import from: common, core, image.core, image.core.cli, image.operators.splitters

Hierarchy within module:
* alpha_splitter_cli
"""

from __future__ import annotations

from .alpha_splitter_cli import AlphaSplitterCli

__all__ = [
    "AlphaSplitterCli",
]
