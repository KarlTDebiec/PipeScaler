#!/usr/bin/env python
#   pipescaler/mergers/alpha_merger.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Matches an image's color histogram to that of a reference image"""
from __future__ import annotations

from logging import info
from typing import Any, List

import numpy as np
from PIL import Image
from skimage.exposure import match_histograms

from pipescaler.core import Merger, validate_image


class ColorMatchMerger(Merger):
    """Matches an image's color histogram to that of a reference image"""

    def __call__(self, outfile: str, **kwargs: Any) -> None:
        self.merge(outfile=outfile, **{k: kwargs.get(k) for k in self.inlets})

    def merge(self, input: str, reference: str, outfile: str) -> None:
        """
        Match an image's color histogram to that of a reference image

        Arguments:
            input: Input image whose color is to be matched
            reference: Reference image to which color is to be matched
            outfile: Output file
        """

        # Read images
        reference_image = validate_image(reference, ["L", "LA", "RGB", "RGBA"])
        input_image = validate_image(input, ["L", "LA", "RGB", "RGBA"])
        if reference_image.mode != input_image.mode:
            raise ValueError(
                f"Image mode '{reference_image.mode}' of image '{reference}'"
                f" does not match mode '{input_image.mode}' of image '{input}'"
            )

        # Merge images
        reference_array = np.array(reference_image)
        input_array = np.array(input_image)
        output_array = match_histograms(
            input_array, reference_array, multichannel=reference_image.mode != "L"
        )
        output_array = np.clip(output_array, 0, 255).astype(np.uint8)
        output_image = Image.fromarray(output_array)

        # Write image
        output_image.save(outfile)
        info(f"'{self}: '{outfile}' saved")

    @property
    def inlets(self) -> List[str]:
        """Inlets that flow into stage"""
        return ["reference", "input"]
