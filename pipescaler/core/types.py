#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Types."""
from pathlib import Path
from typing import Callable

from pipescaler.core.pipelines.pipe_image import PipeImage

PipeFileProcessor = Callable[[Path, Path], None]
"""Function that processes a file."""
PipeMerger = Callable[[PipeImage], PipeImage]
"""Merges two or more PipeImages into a single downstream PipeImage.

Note that this type is identical to PipeProcessor, because in Python f(x) and f(*x) use
the same type annotations.
"""
PipeProcessor = Callable[[PipeImage], PipeImage]
"""Performs operation on a PipeImage, yielding a modified PipeImage."""
PipeSplitter = Callable[[PipeImage], tuple[PipeImage, ...]]
"""Splits one PipeImage into two or more downstream PipeImages."""
