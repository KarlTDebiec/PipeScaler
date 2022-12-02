#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Type hints."""
from pathlib import Path
from typing import Callable, Union

from pipescaler.core.runner import Runner

RunnerLike = Union[Runner, Callable[[Path, Path], None]]
