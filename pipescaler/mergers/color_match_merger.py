#!/usr/bin/env python
#   pipescaler/mergers/alpha_merger.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
""""""
from __future__ import annotations

from logging import info
from typing import Any

import numpy as np
from PIL import Image
from skimage.exposure import match_histograms

from pipescaler.core import Merger, UnsupportedImageModeError, remove_palette_from_image


class ColorMatchMerger(Merger):
    def __call__(self, outfile: str, **kwargs: Any) -> None:
        infiles = {k: kwargs.get(k) for k in self.inlets}

        # Read images
        reference_image = Image.open(infiles["reference"])
        if reference_image.mode == "P":
            reference_image = remove_palette_from_image(reference_image)
        if reference_image.mode not in ("L", "LA", "RGB", "RGBA"):
            raise UnsupportedImageModeError(
                f"Image mode '{reference_image.mode}' of image '{infiles['reference']}'"
                f" is not supported by {type(self)}"
            )
        target_image = Image.open(infiles["target"])
        if target_image.mode == "P":
            target_image = remove_palette_from_image(target_image)
        if target_image.mode not in ("L", "LA", "RGB", "RGBA"):
            raise UnsupportedImageModeError(
                f"Image mode '{target_image.mode}' of image '{infiles['target']}'"
                f" is not supported by {type(self)}"
            )
        if reference_image.mode != target_image.mode:
            raise ValueError(
                f"Image mode '{reference_image.mode}' of image '{infiles['reference']}'"
                f" does not match mode '{target_image.mode}' of image"
                f" '{infiles['target']}'"
            )

        # Merge images
        reference_datum = np.array(reference_image)
        target_datum = np.array(target_image)
        if reference_image.mode == "L":
            output_datum = np.clip(
                match_histograms(target_datum, reference_datum), 0, 255,
            ).astype(np.uint8)
        else:
            output_datum = np.clip(
                match_histograms(target_datum, reference_datum, multichannel=True),
                0,
                255,
            ).astype(np.uint8)
        output_image = Image.fromarray(output_datum)

        # Write image
        output_image.save(outfile)
        info(f"'{self}: '{outfile}' saved")

    @property
    def inlets(self):
        return ["reference", "target"]
