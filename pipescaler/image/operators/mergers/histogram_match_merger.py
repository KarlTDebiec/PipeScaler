#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Matches an image's color histogram to that of a reference image."""
from __future__ import annotations

import numpy as np
from PIL import Image
from skimage.exposure import match_histograms

from pipescaler.image.core import UnsupportedImageModeError
from pipescaler.image.core.operators import ImageMerger
from pipescaler.image.core.validation import validate_image


class HistogramMatchMerger(ImageMerger):
    """Matches an image's color histogram to that of a reference image."""

    def __call__(self, *input_images: Image.Image) -> Image.Image:
        """Merge images.

        Arguments:
            input_images: Input images
        Returns:
            Merged output image
        """
        ref_image = validate_image(input_images[0], self.inputs()["ref"])
        fit_image = validate_image(input_images[1], self.inputs()["fit"])
        if ref_image.mode != fit_image.mode:
            raise UnsupportedImageModeError(
                f"Image mode '{ref_image.mode}' of reference image"
                f" does not match mode '{fit_image.mode}' of fit image"
            )

        ref_array = np.array(ref_image)
        fit_array = np.array(fit_image)
        if ref_image.mode == "L":
            output_array = match_histograms(fit_array, ref_array)
        else:
            output_array = match_histograms(fit_array, ref_array, channel_axis=0)
        output_array = np.clip(output_array, 0, 255).astype(np.uint8)
        output_image = Image.fromarray(output_array)

        return output_image

    @classmethod
    def inputs(cls) -> dict[str, tuple[str, ...]]:
        """Inputs to this operator."""
        return {
            "ref": ("L", "LA", "RGB", "RGBA"),
            "fit": ("L", "LA", "RGB", "RGBA"),
        }

    @classmethod
    def outputs(cls) -> dict[str, tuple[str, ...]]:
        """Outputs of this operator."""
        return {
            "output": ("L", "LA", "RGB", "RGBA"),
        }
