#  Copyright 2020-2023 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Type hints."""
from __future__ import annotations

from pathlib import Path
from typing import Callable

from pipescaler.core.runner import Runner

RunnerLike = Runner | Callable[[Path, Path], None]
