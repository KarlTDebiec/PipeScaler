#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Type hints."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from .runner import Runner

RunnerLike = Runner | Callable[[Path, Path], None]
"""Type alias for a Runner or a callable with the same call signature."""
