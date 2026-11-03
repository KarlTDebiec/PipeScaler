#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Type hints for image processing."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Literal

from PIL import Image

__all__ = ["ImageMode", "ImageWriterLike"]

# Image modes supported by PipeScaler
# 1-bit, grayscale, grayscale+alpha, palette, RGB, RGBA, HSV
# Extend this type if additional modes are needed

type ImageMode = Literal["1", "L", "LA", "P", "RGB", "RGBA", "HSV"]
"""Type alias for supported PIL image mode strings."""

type ImageWriterLike = Callable[[Image.Image, Path], None]
"""Callable that writes in-memory Pillow pixels to an image file."""
