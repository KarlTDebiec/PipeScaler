#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Image functions accelerated with numba."""
from __future__ import annotations

from typing import no_type_check

import numpy as np
from numba import njit


@no_type_check
@njit(nogil=True, cache=True, fastmath=True)
def get_perceptually_weighted_distance(
    color_1: np.ndarray, color_2: np.ndarray
) -> float:
    """Get the squared distance between two colors, adjusted for perception.

    Arguments:
        color_1: Color 1
        color_2: Color 2
    Returns:
        Squared distance between two colors
    """
    rmean = (color_1[0] + color_2[0]) / 2
    dr = color_1[0] - color_2[0]
    dg = color_1[1] - color_2[1]
    db = color_1[2] - color_2[2]
    return (
        ((2 + (rmean / 256)) * (dr**2))
        + (4 * (dg**2))
        + ((2 + ((255 - rmean) / 256)) * (db**2))
    )
