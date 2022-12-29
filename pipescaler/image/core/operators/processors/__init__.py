#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Core image processors."""
from __future__ import annotations

from pipescaler.image.core.operators.processors.pytorch_image_processor import (
    PyTorchImageProcessor,
)

__all__ = [
    "PyTorchImageProcessor",
]
