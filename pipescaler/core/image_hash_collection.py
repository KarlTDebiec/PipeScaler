#!/usr/bin/env python
#  Copyright (C) 2020-2022. Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
from collections.abc import Sequence
from logging import info
from pathlib import Path
from typing import Optional, Union

import numpy as np
import pandas as pd
from imagehash import (
    average_hash,
    colorhash,
    dhash,
    hex_to_flathash,
    hex_to_hash,
    phash,
    whash,
)
from PIL import Image
from scipy.stats import zscore

from pipescaler.common import validate_output_file
from pipescaler.core.pipelines import PipeImage
from pipescaler.pipelines.sorters import AlphaSorter, GrayscaleSorter


class ImageHashCollection(Sequence):
    hash_types = {
        "average": average_hash,
        "color": colorhash,
        "difference": dhash,
        "perceptual": phash,
        "wavelet": whash,
    }

    def __init__(self, file_paths: list[Path], cache: Union[str, Path] = "hashes.csv"):
        """Initialize.

        Arguments:
            file_paths: File paths of images
            cache: Path to cache file
        """
        self.alpha_sorter = AlphaSorter()
        """Alpha sorter."""
        self.grayscale_sorter = GrayscaleSorter()
        """Grayscale sorter."""
        self.hashes = self.get_image_hashes_for_files(file_paths, cache)
        """Image hashes."""

    def __getitem__(self, index: Union[str, tuple[str, float]]) -> pd.DataFrame:
        """Get image hashes matching index.

        Arguments:
            index: Index; if str, return all hashes of that name; if tuple, return all
              hashes of that name at that scale
        Returns:
            Image hash(es) matching index
        """
        if isinstance(index, str):
            return self.hashes.loc[self.hashes["name"] == index]
        elif isinstance(index, tuple):
            return self.hashes.loc[
                (self.hashes["name"] == index[0]) & (self.hashes["scale"] == index[1])
            ]
        else:
            raise TypeError(
                f"Index must be str or tuple of str and float, not {type(index)}"
            )

    def __len__(self) -> int:
        """Get number of image hashes in collection."""
        return len(self.hashes)

    @property
    def full_size(self):
        return self.hashes.loc[(self.hashes["scale"] == 1.0)]

    def get_best_child_score(
        self, parent_hash: pd.Series, scale: float
    ) -> Optional[pd.Series]:
        """Get the best child of provided parent at scale.

        Arguments:
            parent_hash: Parent hash
            scale: Scale of child relative to parent
        Returns:
            Score of the best candidate child of *parent* at *scale*
        """
        # Find the best candidate child
        candidate_child_hashes = self.get_candidate_child_scores(parent_hash, scale)
        if len(candidate_child_hashes) >= 2:
            best_idx = candidate_child_hashes["hamming sum z score"].idxmin()
            if np.isnan(best_idx):
                info(
                    f"Cannot distinguish best child candidate of "
                    f"'{parent_hash['filename']}' from candidates:\n"
                    f"{candidate_child_hashes}"
                )
                return None
            candidate_child_hash = candidate_child_hashes.loc[best_idx]
        elif len(candidate_child_hashes) == 1:
            candidate_child_hash = candidate_child_hashes.iloc[0]
        else:
            return None

        # Find the best candidate parent of candidate child
        candidate_parent_hashes = self.hashes.candidate_parent_scores(
            candidate_child_hash, scale
        )
        if len(candidate_parent_hashes) >= 2:
            best_idx = candidate_parent_hashes["hamming sum z score"].idxmin()
            if np.isnan(best_idx):
                info(
                    f"Cannot distinguish best parent candidate of "
                    f"'{candidate_child_hash}' from candidates:\n"
                    f"{candidate_parent_hashes}"
                )
                return
            candidate_parent_hash = candidate_parent_hashes.loc[best_idx]
        elif len(candidate_parent_hashes) == 1:
            candidate_parent_hash = candidate_parent_hashes.iloc[0]
        else:
            return

        # Review child
        if parent_hash["filename"] == candidate_parent_hash["filename"]:
            if candidate_child_hash["hamming sum"] <= 75:
                return candidate_child_hash
        return

    def get_candidate_child_scores(
        self, parent_hash: pd.Series, scale: float
    ) -> pd.DataFrame:
        """Get scores of all candidate children of provided parent at scale.

        Arguments:
            parent_hash: Parent hash
            scale: Scale of child relative to parent
        Returns:
            Scores of candidate children of *parent* at *scale*
        """
        # Select potential child images
        candidates = self.get_hashes_matching_spec(
            parent_hash["width"] * scale,
            parent_hash["height"] * scale,
            parent_hash["mode"],
            parent_hash["type"],
        )
        if len(candidates) == 0:
            return candidates

        # Calculate hamming distances of candidates and stats
        for hash_type in self.hash_types:
            candidates[f"{hash_type} hamming"] = candidates.apply(
                lambda child_hash: self.hamming_distance(
                    parent_hash, child_hash, hash_type
                ),
                axis=1,
            )
        candidates = self.get_candidate_stats(candidates)

        return candidates

    def get_candidate_parent_scores(
        self, child_hash: pd.Series, scale: float
    ) -> pd.DataFrame:
        """Get scores of all candidate parents of provided child_hash at scale.

        Arguments:
            child_hash: Child hash
            scale: Scale of child relative to parent
        Returns:
            Scores of candidate parents of child at scale
        """
        # Select potential parent images
        candidates = self.get_hashes_matching_spec(
            child_hash["width"] / scale,
            child_hash["height"] / scale,
            child_hash["mode"],
            child_hash["type"],
        )
        if len(candidates) == 0:
            return candidates

        # Calculate hamming distances and stats
        for hash_type in self.hash_types:
            candidates[f"{hash_type} hamming"] = candidates.apply(
                lambda parent_hash: self.hamming_distance(
                    parent_hash, child_hash, hash_type
                ),
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
            [f"{hash_type} hamming" for hash_type in self.hash_types]
        ].sum(axis=1)
        candidates["hamming sum z score"] = zscore(candidates["hamming sum"])
        candidates = candidates.sort_values(["hamming sum z score"])
        candidates["hamming sum z score diff"] = list(
            np.diff(candidates["hamming sum z score"])
        ) + [np.nan]

        return candidates

    def get_hashes_matching_spec(
        self, width: int, height: int, mode: str, type: int
    ) -> pd.DataFrame:
        """Get hashes matching specifications.

        Arguments:
            width: Width of image
            height: Height of image
            mode: Mode of image
            type: Type of image
        Returns:
            Hashes matching specifications
        """
        return self.hashes.loc[
            ((self.hashes["scale"] == 1.0) & self.hashes["width"] == width)
            & (self.hashes["height"] == height)
            & (self.hashes["mode"] == mode)
            & (self.hashes["type"] == type)
        ].copy(deep=True)

    def get_image_hashes_for_file(self, file_path: Path) -> pd.DataFrame:
        """Calculate hashes of image file, including original size and scaled versions.

        Arguments:
            file_path: Path to image file
        Returns:
            Hashes of file, including original size and scaled versions
        """
        image = Image.open(file_path)
        size = image.size
        if self.grayscale_sorter(PipeImage(path=file_path)) == "keep_rgb":
            mode = "RGB"
        else:
            mode = "L"
        if self.alpha_sorter(PipeImage(path=file_path)) == "keep_alpha":
            mode += "A"
        image = image.convert(mode)
        filetype = file_path.stem.split("_")[-1]

        hashes = []
        for scale in np.array([1 / (2**x) for x in range(0, 7)]):
            width = round(size[0] * scale)
            height = round(size[1] * scale)
            if width < 8 or height < 8:
                break
            scaled_image = (
                image.resize((width, height), Image.Resampling.LANCZOS)
                if scale != 1.0
                else image
            )
            scaled_channels = []
            if mode == "L":
                scaled_channels.append(scaled_image)
            elif mode == "LA":
                scaled_channels.append(Image.fromarray(np.array(scaled_image)[:, :, 0]))
                scaled_channels.append(Image.fromarray(np.array(scaled_image)[:, :, 1]))
            elif mode == "RGB":
                scaled_channels.append(Image.fromarray(np.array(scaled_image)[:, :, 0]))
                scaled_channels.append(Image.fromarray(np.array(scaled_image)[:, :, 1]))
                scaled_channels.append(Image.fromarray(np.array(scaled_image)[:, :, 2]))
            elif mode == "RGBA":
                scaled_channels.append(Image.fromarray(np.array(scaled_image)[:, :, 0]))
                scaled_channels.append(Image.fromarray(np.array(scaled_image)[:, :, 1]))
                scaled_channels.append(Image.fromarray(np.array(scaled_image)[:, :, 2]))
                scaled_channels.append(Image.fromarray(np.array(scaled_image)[:, :, 3]))
            hashes.append(
                {
                    **{
                        "name": file_path.stem,
                        "scale": scale,
                        "width": width,
                        "height": height,
                        "mode": mode,
                        "type": filetype,
                    },
                    **{
                        f"{hash_type} hash": "_".join(
                            [str(hash_function(c)) for c in scaled_channels]
                        )
                        for hash_type, hash_function in self.hash_types.items()
                    },
                }
            )

        return pd.DataFrame(hashes)

    def get_image_hashes_for_files(
        self, file_paths: list[Path], cache: Union[str, Path] = "hashes.csv"
    ) -> pd.DataFrame:
        """Calculate hashes for all image files.

        Arguments:
            file_paths: List of paths to image files
            cache: Path to cache file
        Returns:
            Hashes of all image files
        """
        hashes = pd.DataFrame(
            {
                **{
                    "name": pd.Series(dtype="str"),
                    "scale": pd.Series(dtype="float"),
                    "width": pd.Series(dtype="int"),
                    "height": pd.Series(dtype="int"),
                    "mode": pd.Series(dtype="str"),
                    "type": pd.Series(dtype="str"),
                },
                **{
                    f"{hash_type} hash": pd.Series(dtype="str")
                    for hash_type in self.hash_types
                },
            }
        )
        cache = validate_output_file(cache, exists_ok=True)
        if cache.exists():
            hashes = pd.read_csv(cache)
            info(f"Image hashes read from {cache}")

        hashes_changed = False
        hashed_names = set(hashes["name"])
        for file_path in file_paths:
            if file_path.stem not in hashed_names:
                hashes = pd.concat(
                    [
                        hashes,
                        self.get_image_hashes_for_file(file_path),
                    ],
                    ignore_index=True,
                )
                hashed_names.add(file_path.stem)
                hashes_changed = True

        if hashes_changed:
            hashes = hashes.reset_index(drop=True)
            hashes.to_csv(cache, index=False)
            info(f"Image hashes saved to {cache}")

        return hashes

    @staticmethod
    def hamming_distance(
        parent_hash: pd.Series, child_hash: pd.Series, hash_type: str
    ) -> int:
        """Calculate hamming distance of hash_type between parent and child.

        Arguments:
            parent_hash: Parent hash
            child_hash: Child hash
            hash_type: Type of hash
        Returns:
            Hamming distance of hash_type between parent and child
        """
        if hash_type == "color":
            return hex_to_flathash(
                parent_hash[f"{hash_type} hash"], 14
            ) - hex_to_flathash(child_hash[f"{hash_type} hash"], 14)

        return hex_to_hash(parent_hash[f"{hash_type} hash"]) - hex_to_hash(
            child_hash[f"{hash_type} hash"]
        )
