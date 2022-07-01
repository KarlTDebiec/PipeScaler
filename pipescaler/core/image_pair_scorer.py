#!/usr/bin/env python
#  Copyright (C) 2020-2022. Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Image pair scorer."""
from logging import info
from typing import Optional, TypeAlias, Union

import numpy as np
import pandas as pd
from imagehash import hex_to_flathash, hex_to_hash
from scipy.stats import zscore

from pipescaler.core import ImageHashCollection
from pipescaler.core.image_hash_collection import HashSeries
from pipescaler.core.image_pair_collection import PairDataFrame

ScoreDataFrame: TypeAlias = pd.DataFrame


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

    def get_best_child(
        self, parent: Union[str, HashSeries], scale: float
    ) -> Optional[HashSeries]:
        """Get the best child of provided parent at scale.

        Arguments:
            parent: Parent name or hash
            scale: Scale of child relative to parent
        Returns:
            Score of the best candidate child of *parent* at *scale*
        """
        if isinstance(parent, str):
            parent = self.hash_collection[parent, 1.0].iloc[0]
        # Find the best candidate child
        candidate_children = self.get_candidate_children(parent["name"], scale)
        if len(candidate_children) >= 2:
            best_idx = candidate_children["hamming sum z score"].idxmin()
            if np.isnan(best_idx):
                info(
                    f"Cannot distinguish best child candidate of "
                    f"{parent['name']} from candidates:\n"
                    f"{candidate_children}"
                )
                return None
            candidate_child = candidate_children.loc[best_idx]
        elif len(candidate_children) == 1:
            candidate_child = candidate_children.iloc[0]
        else:
            return None

        # Find the best candidate parent of candidate child
        candidate_parents = self.get_candidate_parents(candidate_child, scale)
        if len(candidate_parents) >= 2:
            best_idx = candidate_parents["hamming sum z score"].idxmin()
            if np.isnan(best_idx):
                info(
                    f"Cannot distinguish best parent candidate of "
                    f"{candidate_child['name']} from candidates:\n"
                    f"{candidate_parents}"
                )
                return
            candidate_parent = candidate_parents.loc[best_idx]
        elif len(candidate_parents) == 1:
            candidate_parent = candidate_parents.iloc[0]
        else:
            return

        # Review pair
        if parent["name"] == candidate_parent["name"]:
            if candidate_child["hamming sum"] <= self.thresholds[parent["mode"]][scale]:
                return pd.Series(
                    {
                        "name": parent["name"],
                        "scale": scale,
                        "scaled name": candidate_child["name"],
                        "average hamming": candidate_child["average hamming"],
                        "color hamming": candidate_child["color hamming"],
                        "difference hamming": candidate_child["difference hamming"],
                        "perceptual hamming": candidate_child["perceptual hamming"],
                        "wavelet hamming": candidate_child["wavelet hamming"],
                        "hamming sum": candidate_child["hamming sum"],
                        "hamming sum z score": candidate_child["hamming sum z score"],
                        "hamming sum z score diff": candidate_child[
                            "hamming sum z score diff"
                        ],
                    }
                )
        return

    def get_candidate_children(self, parent: str, scale: float) -> ScoreDataFrame:
        """Get scores of all candidate children of provided parent at scale.

        Arguments:
            parent: Name of parent
            scale: Scale of child relative to parent
        Returns:
            Scores of candidate children of *parent* at *scale*
        """
        parent = self.hash_collection[parent, scale].iloc[0]

        # Select potential child images
        candidates = self.hash_collection.get_hashes_matching_spec(
            parent["width"],
            parent["height"],
            parent["mode"],
            parent["format"],
        )
        if len(candidates) == 0:
            return candidates

        # Calculate hamming distances of candidates and stats
        for hash_type in ["average", "color", "difference", "perceptual", "wavelet"]:
            candidates[f"{hash_type} hamming"] = candidates.apply(
                lambda child: self.hamming_distance(parent, child, hash_type),
                axis=1,
            )
        candidates = self.get_candidate_stats(candidates)

        return candidates

    def get_candidate_parents(
        self, child: Union[str, HashSeries], scale: float
    ) -> ScoreDataFrame:
        """Get scores of all candidate parents of provided child_hash at scale.

        Arguments:
            child: Child hash
            scale: Scale of child relative to parent
        Returns:
            Scores of candidate parents of child at scale
        """
        if isinstance(child, str):
            child = self.hash_collection[child, 1.0].iloc[0]
        # Select potential parent images
        candidates = self.hash_collection.get_hashes_matching_spec(
            child["width"] / scale,
            child["height"] / scale,
            child["mode"],
            child["format"],
        )
        if len(candidates) == 0:
            return candidates

        # Calculate hamming distances and stats
        for hash_type in ["average", "color", "difference", "perceptual", "wavelet"]:
            candidates[f"{hash_type} hamming"] = candidates.apply(
                lambda parent: self.hamming_distance(parent, child, hash_type),
                axis=1,
            )
        candidates = self.get_candidate_stats(candidates)

        return candidates

    def get_candidate_stats(self, candidates: ScoreDataFrame) -> ScoreDataFrame:
        """Get stats of candidate images.

        Arguments:
            candidates: Candidates
        Returns:
            Candidates including statistics
        """
        candidates["hamming sum"] = candidates[
            [
                "average hamming",
                "color hamming",
                "difference hamming",
                "perceptual hamming",
                "wavelet hamming",
            ]
        ].sum(axis=1)
        candidates["hamming sum z score"] = zscore(candidates["hamming sum"])
        candidates = candidates.sort_values(["hamming sum z score"])
        candidates["hamming sum z score diff"] = list(
            np.diff(candidates["hamming sum z score"])
        ) + [np.nan]

        return candidates

    def get_child_score(
        self, parent: Union[str, HashSeries], child: Union[str, HashSeries]
    ) -> pd.Series:
        """Get score of child relative to parent.

        Arguments:
            parent: Parent hash
            child: Child hash
        """
        if isinstance(parent, str):
            parent = self.hash_collection[parent, 1.0].iloc[0]
        if isinstance(child, str):
            child = self.hash_collection[child, 1.0].iloc[0]
        scale = child["width"] / parent["width"]
        candidate_children = self.get_candidate_children(parent["name"], scale)
        score = candidate_children.loc[
            candidate_children["name"] == child["name"]
        ].iloc[0]
        return score

    def get_pair_scores(self, pairs: PairDataFrame) -> ScoreDataFrame:
        scores = []
        for _, pair in pairs.iterrows():

            parent = self.hash_collection[pair["name"], 1.0].iloc[0]
            child = self.hash_collection[pair["scaled name"], 1.0].iloc[0]
            score = self.get_child_score(parent, child)
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
        return pd.DataFrame(scores)

    @staticmethod
    def hamming_distance(parent: HashSeries, child: HashSeries, hash_type: str) -> int:
        """Calculate hamming distance of hash_type between parent and child.

        Arguments:
            parent: Parent hash
            child: Child hash
            hash_type: Type of hash
        Returns:
            Hamming distance of hash_type between parent and child
        """
        if hash_type == "color":
            parent_hash = [
                hex_to_flathash(h, 14) for h in parent[f"{hash_type} hash"].split("_")
            ]
            child_hash = [
                hex_to_flathash(h, 14) for h in child[f"{hash_type} hash"].split("_")
            ]
        else:
            parent_hash = [
                hex_to_hash(h) for h in parent[f"{hash_type} hash"].split("_")
            ]
            child_hash = [hex_to_hash(h) for h in child[f"{hash_type} hash"].split("_")]

        return sum([p - c for p, c in zip(parent_hash, child_hash)])
