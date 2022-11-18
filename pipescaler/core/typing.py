#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
from pathlib import Path
from typing import Callable

from pipescaler.core.pipelines import PipeImage

PipeFileProcessor = Callable[[Path, Path], None]
PipeProcessor = Callable[[PipeImage], PipeImage]
PipeSplitter = Callable[[PipeImage], tuple[PipeImage, ...]]
