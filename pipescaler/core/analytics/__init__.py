#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Analytics."""
from __future__ import annotations

from pipescaler.core.analytics.hashing import (
    multichannel_average_hamming,
    multichannel_average_hash,
    multichannel_color_hamming,
    multichannel_color_hash,
    multichannel_difference_hamming,
    multichannel_difference_hash,
    multichannel_hamming,
    multichannel_hash,
    multichannel_perceptual_hamming,
    multichannel_perceptual_hash,
    multichannel_wavelet_hamming,
    multichannel_wavelet_hash,
)
from pipescaler.core.analytics.typing import (
    HashDataFrame,
    HashSeries,
    PairDataFrame,
    PairSeries,
    ScoreDataFrame,
    ScoreSeries,
    ScoreStatsDataFrame,
    ScoreStatsSeries,
)

__all__ = [
    "HashDataFrame",
    "HashSeries",
    "PairDataFrame",
    "PairSeries",
    "ScoreDataFrame",
    "ScoreSeries",
    "ScoreStatsDataFrame",
    "ScoreStatsSeries",
    "multichannel_average_hamming",
    "multichannel_average_hash",
    "multichannel_color_hamming",
    "multichannel_color_hash",
    "multichannel_difference_hamming",
    "multichannel_difference_hash",
    "multichannel_hamming",
    "multichannel_hash",
    "multichannel_perceptual_hamming",
    "multichannel_perceptual_hash",
    "multichannel_wavelet_hamming",
    "multichannel_wavelet_hash",
]
