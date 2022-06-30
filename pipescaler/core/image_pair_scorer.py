#!/usr/bin/env python
#  Copyright (C) 2020-2022. Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
from logging import info
from typing import Optional, Union

import numpy as np
import pandas as pd
from imagehash import hex_to_flathash, hex_to_hash
from scipy.stats import zscore

from pipescaler.core import ImageHashCollection


class ImagePairScorer:
    def __init__(self, hash_collection: ImageHashCollection):
        """Validate configurate and initialize.

        Arguments:
            hash_collection: Collection of image hashes
        """
        self.hash_collection = hash_collection

    def get_best_child(
        self, parent: Union[str, pd.Series], scale: float
    ) -> Optional[pd.Series]:
        """Get the best child of provided parent at scale.

        Arguments:
            parent: Parent hash
            scale: Scale of child relative to parent
        Returns:
            Score of the best candidate child of *parent* at *scale*
        """
        if isinstance(parent, str):
            parent = self.hash_collection[parent, 1.0].iloc[0]
        # Find the best candidate child
        candidate_children = self.get_candidate_children(parent, scale)
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

        # remove unneeded columns
        candidate_child = candidate_child.drop(
            [
                "scale",
                "width",
                "height",
                "mode",
                "type",
                "average hash",
                "color hash",
                "difference hash",
                "perceptual hash",
                "wavelet hash",
            ]
        )

        # Review pair
        if parent["name"] == candidate_parent["name"]:
            if candidate_child["hamming sum"] <= 75:
                return candidate_child
        return

    def get_candidate_children(
        self, parent: Union[str, pd.Series], scale: float
    ) -> pd.DataFrame:
        """Get scores of all candidate children of provided parent at scale.

        Arguments:
            parent: Parent hash
            scale: Scale of child relative to parent
        Returns:
            Scores of candidate children of *parent* at *scale*
        """
        if isinstance(parent, str):
            parent = self.hash_collection[parent, 1.0].iloc[0]
        # Select potential child images
        candidates = self.hash_collection.get_hashes_matching_spec(
            parent["width"] * scale,
            parent["height"] * scale,
            parent["mode"],
            parent["type"],
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
        self, child: Union[str, pd.Series], scale: float
    ) -> pd.DataFrame:
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
            child["type"],
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

    def get_candidate_stats(self, candidates: pd.DataFrame) -> pd.DataFrame:
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
        self, parent: Union[str, pd.Series], child: Union[str, pd.Series]
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
        candidate_children = self.get_candidate_children(parent, scale)
        score = candidate_children.loc[
            candidate_children["name"] == child["name"]
        ].iloc[0]
        return score

    def get_pair_scores(self, pairs: pd.DataFrame) -> pd.DataFrame:
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
    def hamming_distance(parent: pd.Series, child: pd.Series, hash_type: str) -> int:
        """Calculate hamming distance of hash_type between parent and child.

        Arguments:
            parent: Parent hash
            child: Child hash
            hash_type: Type of hash
        Returns:
            Hamming distance of hash_type between parent and child
        """
        if hash_type == "color":
            parent_hash = hex_to_flathash(parent[f"{hash_type} hash"], 14)
            child_hash = hex_to_flathash(child[f"{hash_type} hash"], 14)
        else:
            parent_hash = hex_to_hash(parent[f"{hash_type} hash"])
            child_hash = hex_to_hash(child[f"{hash_type} hash"])

        return parent_hash - child_hash
