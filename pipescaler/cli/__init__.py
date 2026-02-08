#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PipeScaler general command-line interfaces package.

This module may import from: common, core, pipelines, image, video
"""

from __future__ import annotations

from .pipescaler_cli import PipeScalerCli

__all__ = [
    "PipeScalerCli",
]
