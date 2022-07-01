#!/usr/bin/env python
#  Copyright (C) 2020-2022. Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Image pair scorer."""
from logging import info
from typing import Optional

import numpy as np
import pandas as pd
from scipy.stats import zscore

from pipescaler.core.analytics.aliases import (
    HashDataFrame,
    HashSeries,
    PairDataFrame,
    PairSeries,
    ScoreDataFrame,
    ScoreStatsDataFrame,
    ScoreStatsSeries,
)
from pipescaler.core.analytics.hashing import multichannel_hamming
from pipescaler.core.analytics.image_hash_collection import ImageHashCollection


class ImagePairScorer:
    """Image pair scorer."""

    thresholds = {
        "L": {
            0.50000: 75,
            0.25000: 125,
            0.12500: 175,
            0.06250: 225,
            0.03125: 250,
        },
        "LA": {
            0.50000: 175,
            0.25000: 225,
            0.12500: 275,
            0.06250: 325,
            0.03125: 350,
        },
        "RGB": {
            0.50000: 75,
            0.25000: 125,
            0.12500: 175,
            0.06250: 225,
            0.03125: 250,
        },
        "RGBA": {
            0.50000: 175,
            0.25000: 225,
            0.12500: 275,
            0.06250: 325,
            0.03125: 350,
        },
    }

    def __init__(self, hash_collection: ImageHashCollection):
        """Validate configurate and initialize.

        Arguments:
            hash_collection: Collection of image hashes
        """
        self.hash_collection = hash_collection

    def get_best_child_score_stats(
        self, parent: str, scale: float
    ) -> Optional[ScoreStatsSeries]:
        """Get the best child of provided parent at scale.

        Arguments:
            parent: Parent name
            scale: Scale of child relative to parent
        Returns:
            Score of the best candidate child of *parent* at *scale*
        """
        # Find the best candidate child
        candidate_children: Optional[ScoreStatsDataFrame] = self.get_candidate_children(
            parent, scale
        )
        if candidate_children is None or len(candidate_children) == 0:
            return None
        if len(candidate_children) == 1:
            candidate_child: ScoreStatsSeries = candidate_children.iloc[0]
        else:
            best_idx = candidate_children["hamming sum z score"].idxmin()
            if (
                np.isnan(best_idx)
                or candidate_children["hamming sum z score"].value_counts()[
                    candidate_children["hamming sum z score"].min()
                ]
                > 1
            ):
                info(
                    f"Cannot distinguish best child candidate of {parent} "
                    f"among candidates:\n"
                    f"{candidate_children}"
                )
                return None
            candidate_child: ScoreStatsSeries = candidate_children.loc[best_idx]

        # Find the best candidate parent of candidate child
        candidate_parents: Optional[ScoreStatsDataFrame] = self.get_candidate_parents(
            candidate_child["scaled name"], scale
        )
        if candidate_parents is None or len(candidate_parents) == 0:
            return None
        if len(candidate_parents) == 1:
            candidate_parent: ScoreStatsSeries = candidate_parents.iloc[0]
        else:
            best_idx = candidate_parents["hamming sum z score"].idxmin()
            if np.isnan(best_idx):
                info(
                    f"Cannot distinguish best parent candidate of "
                    f"{candidate_child['name']} from candidates:\n"
                    f"{candidate_parents}"
                )
                return None
            candidate_parent: ScoreStatsSeries = candidate_parents.loc[best_idx]

        # Review pair
        if parent == candidate_parent["name"]:
            candidate_parent: HashSeries = self.hash_collection[
                candidate_parent["name"], scale
            ].iloc[0]
            threshold = self.thresholds[candidate_parent["mode"]][scale]
            if candidate_child["hamming sum"] <= threshold:
                return candidate_child
            return None
        info(
            f"{candidate_child['scaled name']} identified as best candidate child of "
            f"{parent} at {scale}, however {candidate_child['scaled name']} has a "
            f"better candidate parent, {candidate_parent['name']}."
        )
        return None

    def get_candidate_children(
        self, parent: str, scale: float
    ) -> Optional[ScoreStatsDataFrame]:
        """Get scores of all candidate children of provided parent at scale.

        Arguments:
            parent: Name of parent
            scale: Scale of child relative to parent
        Returns:
            Scores of candidate children of parent at scale
        """
        parent: HashSeries = self.hash_collection[parent, scale].iloc[0]
        average = lambda child: multichannel_hamming(parent, child, "average")
        color = lambda child: multichannel_hamming(parent, child, "color")
        difference = lambda child: multichannel_hamming(parent, child, "difference")
        perceptual = lambda child: multichannel_hamming(parent, child, "perceptual")
        wavelet = lambda child: multichannel_hamming(parent, child, "wavelet")

        # Select potential child images
        candidates: HashDataFrame = self.hash_collection.get_hashes_matching_spec(
            parent["width"],
            parent["height"],
            parent["mode"],
            parent["format"],
        )
        if len(candidates) == 0:
            return None

        # Calculate hamming distances of candidates and stats
        candidate_scores: ScoreDataFrame = pd.DataFrame(
            {
                "name": parent["name"],
                "scale": scale,
                "scaled name": candidates["name"],
                "average hamming": candidates.apply(average, axis=1),
                "color hamming": candidates.apply(color, axis=1),
                "difference hamming": candidates.apply(difference, axis=1),
                "perceptual hamming": candidates.apply(perceptual, axis=1),
                "wavelet hamming": candidates.apply(wavelet, axis=1),
            }
        )
        candidate_score_stats: ScoreStatsDataFrame = self.get_stats(candidate_scores)

        return candidate_score_stats

    def get_candidate_parents(
        self, child: str, scale: float
    ) -> Optional[ScoreStatsDataFrame]:
        """Get scores of all candidate parents of provided child_hash at scale.

        Arguments:
            child: Child hash
            scale: Scale of child relative to parent
        Returns:
            Scores of candidate parents of child at scale
        """
        child: HashSeries = self.hash_collection[child, 1.0].iloc[0]
        average = lambda parent: multichannel_hamming(parent, child, "average")
        color = lambda parent: multichannel_hamming(parent, child, "color")
        difference = lambda parent: multichannel_hamming(parent, child, "difference")
        perceptual = lambda parent: multichannel_hamming(parent, child, "perceptual")
        wavelet = lambda parent: multichannel_hamming(parent, child, "wavelet")

        # Select potential parent images
        candidates: HashDataFrame = self.hash_collection.get_hashes_matching_spec(
            round(child["width"] / scale),
            round(child["height"] / scale),
            child["mode"],
            child["format"],
        )
        if len(candidates) == 0:
            return None

        # Calculate hamming distances and stats
        candidate_scores: ScoreDataFrame = pd.DataFrame(
            {
                "name": candidates["name"],
                "scale": scale,
                "scaled name": child["name"],
                "average hamming": candidates.apply(average, axis=1),
                "color hamming": candidates.apply(color, axis=1),
                "difference hamming": candidates.apply(difference, axis=1),
                "perceptual hamming": candidates.apply(perceptual, axis=1),
                "wavelet hamming": candidates.apply(wavelet, axis=1),
            }
        )
        candidate_score_stats: ScoreStatsDataFrame = self.get_stats(candidate_scores)

        return candidate_score_stats

    def get_pair_score_stats(self, pair: PairSeries) -> ScoreStatsSeries:
        """Get score of child relative to parent.

        Arguments:
            pair: pair to get score of
        Returns:
            Score of pair
        """
        candidate_children: ScoreStatsDataFrame = self.get_candidate_children(
            pair["name"], pair["scale"]
        )
        score: ScoreStatsSeries = candidate_children.loc[
            candidate_children["scaled name"] == pair["scaled name"]
        ].iloc[0]

        return score

    def get_pair_scores(self, pairs: PairDataFrame) -> ScoreDataFrame:
        scores = []
        for _, pair in pairs.iterrows():
            score = self.get_pair_score_stats(pair)
            scores.append(
                {
                    "name": pair["name"],
                    "scale": pair["scale"],
                    "scaled name": pair["scaled name"],
                    "average hamming": score["average hamming"],
                    "color hamming": score["color hamming"],
                    "difference hamming": score["difference hamming"],
                    "perceptual hamming": score["perceptual hamming"],
                    "wavelet hamming": score["wavelet hamming"],
                    "hamming sum": score["hamming sum"],
                    "hamming sum z score": score["hamming sum z score"],
                    "hamming sum z score diff:": score["hamming sum z score diff"],
                }
            )
        scores = pd.DataFrame(scores)

        return scores

    @staticmethod
    def get_stats(scores: ScoreDataFrame) -> ScoreStatsDataFrame:
        """Get stats of candidate images.

        Arguments:
            scores: Candidate scores
        Returns:
            Candidates including statistics
        """
        stats = scores.copy()
        stats["hamming sum"] = stats[
            [
                "average hamming",
                "color hamming",
                "difference hamming",
                "perceptual hamming",
                "wavelet hamming",
            ]
        ].sum(axis=1)
        stats["hamming sum z score"] = zscore(stats["hamming sum"])
        stats = stats.sort_values(["hamming sum z score"])
        stats["hamming sum z score diff"] = list(
            np.diff(stats["hamming sum z score"])
        ) + [np.nan]

        return stats
