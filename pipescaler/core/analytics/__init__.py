#!/usr/bin/env python
#  Copyright (C) 2020-2022. Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Core pipescaler analytics classes."""
from __future__ import annotations

from pipescaler.core.analytics.aliases import (
    HashDataFrame,
    HashSeries,
    PairDataFrame,
    PairSeries,
    ScoreDataFrame,
    ScoreSeries,
    ScoreStatsDataFrame,
    ScoreStatsSeries,
)
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
from pipescaler.core.analytics.image_hash_collection import ImageHashCollection
from pipescaler.core.analytics.image_pair_collection import ImagePairCollection
from pipescaler.core.analytics.image_pair_scorer import ImagePairScorer

__all__: list[str] = [
    "HashDataFrame",
    "HashSeries",
    "ImageHashCollection",
    "ImagePairCollection",
    "ImagePairScorer",
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
