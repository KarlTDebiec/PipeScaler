#!/usr/bin/env python
#  Copyright 2020-2023 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""PipeScaler image package; contains code specific to image processing."""
from __future__ import annotations

from pipescaler.image.scaled_pair_identifier import ScaledPairIdentifier
from pipescaler.image.subdivided_image import SubdividedImage
from pipescaler.image.testing import (
    get_expected_output_mode,
    xfail_unsupported_image_mode,
)

__all__ = [
    "get_expected_output_mode",
    "xfail_unsupported_image_mode",
    "ScaledPairIdentifier",
    "SubdividedImage",
]
