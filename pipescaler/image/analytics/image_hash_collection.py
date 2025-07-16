#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Collection of image hashes."""

from __future__ import annotations

from collections.abc import Collection, Iterable, Sequence
from logging import info
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image

from pipescaler.common.typing import PathLike
from pipescaler.common.validation import validate_output_file
from pipescaler.image.core.analytics.hashing import (
    multichannel_average_hash,
    multichannel_color_hash,
    multichannel_difference_hash,
    multichannel_perceptual_hash,
    multichannel_wavelet_hash,
)
from pipescaler.image.core.analytics.typing import HashDataFrame
from pipescaler.image.core.pipelines import PipeImage
from pipescaler.image.pipelines.sorters import AlphaSorter, GrayscaleSorter


class ImageHashCollection(Sequence):
    """Collection of image hashes."""

    def __init__(self, file_paths: Collection[Path], cache: PathLike = "hashes.csv"):
        """Validate configuration and initialize.

        Arguments:
            file_paths: File paths of images
            cache: Path to cache file
        """
        self.alpha_sorter = AlphaSorter()
        """Alpha sorter."""
        self.grayscale_sorter = GrayscaleSorter()
        """Grayscale sorter."""

        self.cache = validate_output_file(cache, may_exist=True)
        """CSV cache file path."""

        # Prepare image hashes
        self._hashes = None
        self.load_cache()
        hashes_changed = False
        hashed_names = set(self.hashes["name"])
        for file_path in file_paths:
            if file_path.stem not in hashed_names:
                self.add(file_path)
                hashed_names.add(file_path.stem)
                hashes_changed = True
        if hashes_changed:
            self.save_cache()

    def __getitem__(
        self,
        index: str | tuple[str, float] | Iterable[str | tuple[str, float]],
    ) -> HashDataFrame:
        """Get image hashes matching index.

        Arguments:
            index: Name or names for which to return hashes
        Returns:
            Image hashes matching index
        """
        if isinstance(index, str):
            return self.hashes.loc[self.hashes["name"] == index]
        if isinstance(index, tuple):
            return self.hashes.loc[
                (self.hashes["name"] == index[0]) & (self.hashes["scale"] == index[1])
            ]
        if isinstance(index, Iterable):
            return pd.concat([self[i] for i in index])
        raise TypeError(
            f"Index must be str, tuple of str and float, or iterable thereof, "
            f"not {type(index)}"
        )

    def __len__(self) -> int:
        """Number of image hashes in collection."""
        return len(self.hashes)

    @property
    def full_size_hashes(self) -> HashDataFrame:
        """Full size image hashes."""
        return self.hashes.loc[(self.hashes["scale"] == 1.0)]

    @property
    def hashes(self) -> HashDataFrame:
        """Image hashes."""
        if self._hashes is None:
            self._hashes = pd.DataFrame(
                {
                    "name": pd.Series(dtype="str"),
                    "scale": pd.Series(dtype="float"),
                    "width": pd.Series(dtype="int"),
                    "height": pd.Series(dtype="int"),
                    "mode": pd.Series(dtype="str"),
                    "format": pd.Series(dtype="str"),
                    "average hash": pd.Series(dtype="str"),
                    "color hash": pd.Series(dtype="str"),
                    "difference hash": pd.Series(dtype="str"),
                    "perceptual hash": pd.Series(dtype="str"),
                    "wavelet hash": pd.Series(dtype="str"),
                }
            )
        return self._hashes

    @hashes.setter
    def hashes(self, value: HashDataFrame) -> None:
        if value.columns.tolist() != self.hashes.columns.tolist():
            raise ValueError(
                f"hashes must have columns {self.hashes.columns.tolist()}, not "
                f"{value.columns.tolist()}"
            )
        self._hashes = value

    def add(self, file_path: Path) -> None:
        """Add image hash to collection.

        Arguments:
            file_path: File path of image whose hashes to add
        """
        pipe_image = PipeImage(path=file_path)
        if self.grayscale_sorter(pipe_image) == "keep_rgb":
            mode = "RGB"
        else:
            mode = "L"
        if self.alpha_sorter(pipe_image) == "keep_alpha":
            mode += "A"
        if pipe_image.image.mode != mode:
            pipe_image.image = pipe_image.image.convert(mode)

        new_row = self.multiscale_multifunction_hash(pipe_image)

        self.hashes = pd.concat([self.hashes, new_row], ignore_index=True)

    def get_hashes_matching_spec(
        self, width: int, height: int, mode: str, image_format: int
    ) -> HashDataFrame:
        """Get hashes matching specifications.

        Arguments:
            width: Width of image
            height: Height of image
            mode: Mode of image
            image_format: Format of image
        Returns:
            Hashes matching specifications
        """
        matches = self.hashes.loc[
            (self.hashes["scale"] == 1.0)
            & (self.hashes["width"] == width)
            & (self.hashes["height"] == height)
            & (self.hashes["mode"] == mode)
            & (self.hashes["format"] == image_format)
        ]
        return matches.copy(deep=True)

    def load_cache(self) -> None:
        """Load image hashes from cache."""
        if self.cache.exists():
            self.hashes = pd.read_csv(self.cache)
            info(f"Image hashes read from {self.cache}")

    def save_cache(self) -> None:
        """Save image hashes to cache file."""
        self.hashes = self.hashes.reset_index(drop=True)
        self.hashes.to_csv(self.cache, index=False)
        info(f"Image hashes saved to {self.cache}")

    @staticmethod
    def multiscale_multifunction_hash(pipe_image: PipeImage) -> HashDataFrame:
        """Calculate hashes of image, including original size and scaled versions.

        Arguments:
            pipe_image: Image of which to calculate hashes
        Returns:
            Image hashes
        """
        width, height = pipe_image.image.size
        image_format = pipe_image.name.split("_")[-1]

        hashes = []
        for scale in np.array([1 / (2**x) for x in range(0, 7)]):
            # Prepare image or scaled version of image
            if scale == 1.0:
                scaled_width = width
                scaled_height = height
                scaled_image = pipe_image.image
            else:
                scaled_width = round(width * scale)
                scaled_height = round(height * scale)
                if scaled_width < 8 or scaled_height < 8:
                    break
                scaled_image = pipe_image.image.resize(
                    (scaled_width, scaled_height),
                    Image.Resampling.LANCZOS,  # type: ignore
                )

            # Calculate hashes of channels of scaled image
            hashes.append(
                {
                    "name": pipe_image.name,
                    "scale": scale,
                    "width": scaled_width,
                    "height": scaled_height,
                    "mode": scaled_image.mode,
                    "format": image_format,
                    "average hash": multichannel_average_hash(scaled_image),
                    "color hash": multichannel_color_hash(scaled_image),
                    "difference hash": multichannel_difference_hash(scaled_image),
                    "perceptual hash": multichannel_perceptual_hash(scaled_image),
                    "wavelet hash": multichannel_wavelet_hash(scaled_image),
                }
            )

        return pd.DataFrame(hashes)
