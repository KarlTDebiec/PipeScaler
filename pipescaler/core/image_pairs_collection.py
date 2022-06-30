#!/usr/bin/env python
#  Copyright (C) 2020-2022. Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
from collections.abc import Sequence
from logging import info
from pathlib import Path
from typing import Union

import pandas as pd

from pipescaler.common import validate_output_file


class ImagePairsCollection(Sequence):
    def __init__(self, cache: Union[str, Path] = "pairs.csv") -> None:
        self.cache = validate_output_file(cache, exists_ok=True)
        """CSV file from which to read/write scaled image pairs."""

        self.pairs = self.nay(cache)

    def __getitem__(self, index: Union[str, tuple[str, str]]) -> pd.DataFrame:
        if isinstance(index, str):
            return self.pairs.loc[self.pairs["name"] == index]
        elif isinstance(index, tuple):
            return self.pairs.loc[
                (self.pairs["name"] == index[0])
                & (self.pairs["scaled name"] == index[1])
            ]
        else:
            raise TypeError(
                f"Index must be str or tuple of str and str, not {type(index)}"
            )

    def __len__(self) -> int:
        return len(self.pairs)

    @property
    def children(self) -> set[str]:
        """Child images."""
        return set(self.pairs["scaled name"])

    @property
    def parents(self) -> set[str]:
        """Parent images."""
        return set(self.pairs["name"])

    def get_pair(self, child: str) -> pd.DataFrame:
        """Get pair of child.

        Arguments:
            child: Basename of child
        Returns:
            Pair of child
        """
        return self.pairs.loc[self.pairs["scaled filename"] == child]

    def get_pairs(self, parent: str) -> pd.DataFrame:
        """Get pairs of parent.

        Arguments:
            parent: Basename of parent
        Returns:
            Pairs of *parent*
        """
        return self.pairs.loc[self.pairs["filename"] == parent]

    def nay(self, cache: Union[str, Path] = "pairs.csv") -> pd.DataFrame:
        pairs = pd.DataFrame(
            {
                "name": pd.Series(dtype="str"),
                "scale": pd.Series(dtype="float"),
                "scaled name": pd.Series(dtype="str"),
            }
        )
        cache = validate_output_file(cache, exists_ok=True)
        if cache.exists():
            pairs = pd.read_csv(cache)
            info(f"Image pairs read from {cache}")

        return pairs
