#!/usr/bin/env python
#  Copyright (C) 2020-2022. Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Collection of image pairs."""
from collections.abc import Sequence
from logging import info
from pathlib import Path
from typing import Iterable, Union

import pandas as pd

from pipescaler.common import validate_output_file


class ImagePairsCollection(Sequence):
    """Collection of image pairs."""

    def __init__(self, cache: Union[str, Path] = "pairs.csv") -> None:
        """Validate configuration and initialize.

        Arguments:
            cache: Path to cache file
        """
        self.cache = validate_output_file(cache, exists_ok=True)
        """CSV file from which to read/write scaled image pairs."""

        # Prepare image pairs
        self._pairs = None
        if self.cache.exists():
            self.pairs = pd.read_csv(self.cache)
            info(f"Image pairs read from {self.cache}")

    def __getitem__(self, index: Union[str, Iterable[str]]) -> pd.DataFrame:
        """Get image pairs matching index.

        Arguments
            index: Name or names for which to return pairs
        Returns:
            Image pairs matching index
        """
        if isinstance(index, str):
            return self.pairs.loc[self.pairs["name"] == index]
        if isinstance(index, Iterable):
            return self.pairs.loc[self.pairs["name"].isin(index)]
        raise TypeError(f"Index must be str or iterable of str, not {type(index)}")

    def __len__(self) -> int:
        """Get number of pairs in collection."""
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
    def pairs(self) -> pd.DataFrame:
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
    def pairs(self, value: pd.DataFrame) -> None:
        if value.columns.tolist() != self.pairs.columns.tolist():
            raise ValueError(
                f"pairs must have columns {self.pairs.columns.tolist()}, not "
                f"{value.columns.tolist()}"
            )
        self._pairs = value

    def add(self, pairs: pd.DataFrame):
        """Add pairs to collection.

        Arguments:
            pairs: Pairs to add
        """
        # TODO: Validate that pair does not already exist
        # TODO: Validate that child is not already in a pair
        self.pairs = pd.concat([self.pairs, pairs], ignore_index=True)

    def get_pair_for_child(self, child: str) -> pd.DataFrame:
        """Get pair of child.

        Arguments:
            child: Basename of child
        Returns:
            Pair of child
        """
        return self.pairs.loc[self.pairs["scaled filename"] == child]

    def get_pairs_for_parent(self, parent: str) -> pd.DataFrame:
        """Get pairs of parent.

        Arguments:
            parent: Basename of parent
        Returns:
            Pairs of *parent*
        """
        return self.pairs.loc[self.pairs["filename"] == parent]

    def save_cache(self):
        """Save image hashes to cache file."""
        self.pairs = self.pairs.reset_index(drop=True).sort_values(
            ["name", "scale"], ascending=False
        )
        self.pairs.to_csv(self.cache, index=False)
        info(f"Image pairs saved to {self.cache}")
