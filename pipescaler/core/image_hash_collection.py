#!/usr/bin/env python
#  Copyright (C) 2020-2022. Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
from collections.abc import Sequence
from logging import info
from pathlib import Path
from typing import Union

import numpy as np
import pandas as pd
from imagehash import average_hash, colorhash, dhash, phash, whash
from PIL import Image

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
        self.alpha_sorter = AlphaSorter()
        """Alpha sorter."""
        self.grayscale_sorter = GrayscaleSorter()
        """Grayscale sorter."""
        self.hashes = self.get_hashes_for_file_paths(file_paths, cache)

    def __getitem__(self, index: Union[str, tuple[str, float]]) -> dict:
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
        return len(self.hashes)

    def get_hashes_for_file_paths(
        self, file_paths: list[Path], cache: Union[str, Path] = "hashes.csv"
    ) -> pd.DataFrame:
        """Calculate hashes for all image files."""
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
                        self.get_hashes_for_file_path(file_path),
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

    def get_hashes_for_file_path(self, file_path: Path) -> pd.DataFrame:
        """Calculate hashes of image file, including original size and scaled versions.

        Arguments:
            file_path: Path to image file
        Returns:
            Hashes of file, including original size and scaled versions
        """
        image = Image.open(file_path)
        size = image.size
        if self.grayscale_sorter(PipeImage(image)) == "keep_rgb":
            mode = "RGB"
        else:
            mode = "L"
        if self.alpha_sorter(PipeImage(image)) == "keep_alpha":
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
