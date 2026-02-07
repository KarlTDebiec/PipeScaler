#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core image analytics hashing."""

from __future__ import annotations

from collections.abc import Callable
from functools import partial

from imagehash import (
    ImageHash,
    average_hash,
    colorhash,
    dhash,
    hex_to_flathash,
    hex_to_hash,
    phash,
    whash,
)
from PIL import Image

from .typing import HashSeries


def multichannel_hamming(first: HashSeries, second: HashSeries, hash_type: str) -> int:
    """Calculate hamming distance of hash_type between two hashes.

    Arguments:
        first: First hash series
        second: Second hash series
        hash_type: Type of hash
    Returns:
        Hamming distance of hash_type between first and second hashes
    """
    if hash_type == "color":
        first_hash = [
            hex_to_flathash(h, 14) for h in first[f"{hash_type} hash"].split("_")
        ]
        second_hash = [
            hex_to_flathash(h, 14) for h in second[f"{hash_type} hash"].split("_")
        ]
    else:
        first_hash = [hex_to_hash(h) for h in first[f"{hash_type} hash"].split("_")]
        second_hash = [hex_to_hash(h) for h in second[f"{hash_type} hash"].split("_")]

    return sum(p - c for p, c in zip(first_hash, second_hash))


multichannel_average_hamming = partial(multichannel_hamming, hash_type="average")
"""Calculate average hamming distance between two hashes."""

multichannel_color_hamming = partial(multichannel_hamming, hash_type="color")
"""Calculate color hamming distance between two hashes."""

multichannel_difference_hamming = partial(multichannel_hamming, hash_type="difference")
"""Calculate difference hamming distance between two hashes."""

multichannel_perceptual_hamming = partial(multichannel_hamming, hash_type="perceptual")
"""Calculate perceptual hamming distance between two hashes."""

multichannel_wavelet_hamming = partial(multichannel_hamming, hash_type="wavelet")
"""Calculate wavelet hamming distance between two hashes."""


def multichannel_hash(
    image: Image.Image,
    hash_function: Callable[[Image.Image], ImageHash],
) -> str:
    """Hash image channels separately and return as an underscore-delimited str."""
    return "_".join([str(hash_function(c)) for c in image.split()])


multichannel_average_hash = partial(multichannel_hash, hash_function=average_hash)
"""Average hash image channels and return as an underscore-delimited str."""
multichannel_color_hash = partial(multichannel_hash, hash_function=colorhash)
"""Color hash image channels and return as an underscore-delimited str."""
multichannel_difference_hash = partial(multichannel_hash, hash_function=dhash)
"""Difference hash image channels and return as an underscore-delimited str."""
multichannel_perceptual_hash = partial(multichannel_hash, hash_function=phash)
"""Perceptual hash image channels and return as an underscore-delimited str."""
multichannel_wavelet_hash = partial(multichannel_hash, hash_function=whash)
"""Wavelet hash image channels and return as an underscore-delimited str."""
