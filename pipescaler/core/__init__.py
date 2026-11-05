#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PipeScaler general core package.

This module may import from: common

Package hierarchy (modules may import from any above):
* exceptions / runner / sorting / utility
* dependencies / typing
* pipelines
"""

from __future__ import annotations

from .exceptions import DependencyError, PipeScalerError
from .runner import Runner
from .typing import RunnerLike
from .utility import Utility

__all__ = [
    "DependencyError",
    "PipeScalerError",
    "Runner",
    "RunnerLike",
    "Utility",
]
