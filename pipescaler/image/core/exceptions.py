#  Copyright 2020-2023 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Image exceptions."""
from __future__ import annotations


class UnsupportedImageModeError(Exception):
    """Mode of image is not supported."""
