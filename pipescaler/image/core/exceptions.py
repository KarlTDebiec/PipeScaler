#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Image exceptions."""

from __future__ import annotations

from pipescaler.core.exceptions import PipeScalerError

__all__ = ["UnsupportedImageModeError"]


class UnsupportedImageModeError(PipeScalerError):
    """Mode of image is not supported."""
