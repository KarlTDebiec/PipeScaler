#!/usr/bin/env python
#   pipescaler/mergers/alpha_merger.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
from __future__ import annotations

from logging import info
from typing import Any

import numpy as np
from PIL import Image
from skimage.exposure import match_histograms

from pipescaler.core import Merger, validate_image


class ColorMatchMerger(Merger):
    """Matches an image's color histogram to that of a reference image."""

    def __call__(self, outfile: str, **kwargs: Any) -> None:
        infiles = {k: kwargs.get(k) for k in self.inlets}

        # Read images
        reference_image = validate_image(
            infiles["reference"], ["L", "LA", "RGB", "RGBA"]
        )
        input_image = validate_image(infiles["input"], ["L", "LA", "RGB", "RGBA"])
        if reference_image.mode != input_image.mode:
            raise ValueError(
                f"Image mode '{reference_image.mode}' of image '{infiles['reference']}'"
                f" does not match mode '{input_image.mode}' of image"
                f" '{infiles['input']}'"
            )

        # Merge images
        reference_datum = np.array(reference_image)
        input_datum = np.array(input_image)
        if reference_image.mode == "L":
            output_datum = match_histograms(
                input_datum, reference_datum, multichannel=False
            )
        else:
            output_datum = match_histograms(
                input_datum, reference_datum, multichannel=True
            )
        output_image = Image.fromarray(np.clip(output_datum, 0, 255,).astype(np.uint8))

        # Write image
        output_image.save(outfile)
        info(f"'{self}: '{outfile}' saved")

    @property
    def inlets(self):
        return ["reference", "input"]
