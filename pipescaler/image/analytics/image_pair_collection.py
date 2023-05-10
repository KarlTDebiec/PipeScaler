#!/usr/bin/env python
#  Copyright 2020-2023 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Collection of image pairs _."""
from __future__ import annotations

from collections.abc import Sequence
from logging import info
from typing import Iterable

import pandas as pd

from pipescaler.common import PathLike, validate_output_file
from pipescaler.image.core.analytics import PairDataFrame


class ImagePairCollection(Sequence):
    """Collection of image pairs."""

    def __init__(self, cache: PathLike = "pairs.csv") -> None:
        """Validate configuration and initialize.

        Arguments:
            cache: Path to cache file
        """
        self.cache = validate_output_file(cache, may_exist=True)
        """CSV cache file path."""

        # Prepare image pairs
        self._pairs = None
        self.load_cache()

    def __getitem__(self, index: str | Iterable[str]) -> PairDataFrame:
        """Get image pairs matching index.

        Arguments:
            index: Name or names for which to return pairs
        Returns:
            Image pairs matching index
        """
        if isinstance(index, str):
            return self.pairs.loc[self.pairs["name"] == index]
        if isinstance(index, Iterable):
            return self.pairs.loc[self.pairs["name"].isin(index)]
        raise TypeError(f"Index must be str or iterable thereof, not {type(index)}")

    def __len__(self) -> int:
        """Number of image pairs in collection."""
        return len(self.pairs)

    @property
    def children(self) -> set[str]:
        """Child images."""
        return set(self.pairs["scaled name"])

    @property
    def parents(self) -> set[str]:
        """Parent images."""
        return set(self.pairs["name"])

    @property
    def pairs(self) -> PairDataFrame:
        """Pairs of images."""
        if self._pairs is None:
            self._pairs = pd.DataFrame(
                {
                    "name": pd.Series(dtype="str"),
                    "scale": pd.Series(dtype="float"),
                    "scaled name": pd.Series(dtype="str"),
                }
            )
        return self._pairs

    @pairs.setter
    def pairs(self, value: PairDataFrame) -> None:
        if value.columns.tolist() != self.pairs.columns.tolist():
            raise ValueError(
                f"pairs must have columns {self.pairs.columns.tolist()}, not "
                f"{value.columns.tolist()}"
            )
        self._pairs = value

    def add(self, pairs: PairDataFrame) -> None:
        """Add pairs to collection.

        Arguments:
            pairs: Pairs to add
        """
        # TODO: Validate that pair does not already exist
        # TODO: Validate that child is not already in a pair
        self.pairs = pd.concat([self.pairs, pairs], ignore_index=True)

    def get_pair_for_child(self, child: str) -> PairDataFrame:
        """Get pair of child.

        Arguments:
            child: Basename of child
        Returns:
            Pair of child
        """
        return self.pairs.loc[self.pairs["scaled filename"] == child]

    def get_pairs_for_parent(self, parent: str) -> PairDataFrame:
        """Get pairs of parent.

        Arguments:
            parent: Basename of parent
        Returns:
            Pairs of parent
        """
        return self.pairs.loc[self.pairs["filename"] == parent]

    def load_cache(self) -> None:
        """Load image pairs from cache file."""
        if self.cache.exists():
            self.pairs = pd.read_csv(self.cache)
            info(f"Image pairs read from {self.cache}")

    def save_cache(self) -> None:
        """Save image pairs to cache file."""
        self.pairs = self.pairs.reset_index(drop=True).sort_values(
            ["name", "scale"], ascending=False
        )
        self.pairs.to_csv(self.cache, index=False)
        info(f"Image pairs saved to {self.cache}")
