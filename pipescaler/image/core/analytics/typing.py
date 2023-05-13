#!/usr/bin/env python
#  Copyright 2020-2023 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core image analytics types."""
from __future__ import annotations

from typing import TypeAlias

import pandas as pd

HashDataFrame: TypeAlias = pd.DataFrame
HashSeries: TypeAlias = pd.Series
PairDataFrame: TypeAlias = pd.DataFrame
PairSeries: TypeAlias = pd.Series
ScoreDataFrame: TypeAlias = pd.DataFrame
ScoreSeries: TypeAlias = pd.Series
ScoreStatsDataFrame: TypeAlias = pd.DataFrame
ScoreStatsSeries: TypeAlias = pd.Series
