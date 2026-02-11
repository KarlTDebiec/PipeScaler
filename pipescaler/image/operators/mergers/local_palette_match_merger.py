#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Matches an image's palette to nearby colors from a reference image."""

from __future__ import annotations

from logging import warning
from typing import Any

from PIL import Image

from pipescaler.common.validation import val_int
from pipescaler.image.core import UnsupportedImageModeError
from pipescaler.image.core.operators import ImageMerger
from pipescaler.image.core.typing import ImageMode
from pipescaler.image.core.validation import validate_image
from pipescaler.image.utilities import LocalPaletteMatcher, LocalPaletteShaderMatcher
from pipescaler.image.utilities.local_palette_shader_matcher import (
    LocalPaletteShaderError,
)


class LocalPaletteMatchMerger(ImageMerger):
    """Matches an image's palette to nearby colors from a reference image."""

    def __init__(self, local_range: int = 1, **kwargs: Any):
        """Validate configuration and initialize.

        Arguments:
            local_range: Range of adjacent pixels from which to draw best-fit color;
              1 checks a 3x3 window, 2 checks a 5x5 window, etc.
            **kwargs: Additional keyword arguments passed to ImageMerger
        """
        super().__init__(**kwargs)
        self.local_range = val_int(local_range, min_value=1)

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
                f"Image mode '{ref_image.mode}' of reference image does not match mode "
                f"'{fit_image.mode}' of fit image"
            )

        try:
            return LocalPaletteShaderMatcher.run(
                ref_image,
                fit_image,
                self.local_range,
            )
        except LocalPaletteShaderError as exc:
            warning(
                f"{self.__class__.__name__}: Shader path unavailable ('{exc}'); "
                "falling back to CPU local matcher."
            )
            return LocalPaletteMatcher.run(ref_image, fit_image, self.local_range)

    def __repr__(self) -> str:
        """Representation."""
        return f"{self.__class__.__name__}(local_range={self.local_range!r})"

    @classmethod
    def inputs(cls) -> dict[str, tuple[ImageMode, ...]]:
        """Inputs to this operator."""
        return {
            "ref": ("L", "RGB"),
            "fit": ("L", "RGB"),
        }

    @classmethod
    def outputs(cls) -> dict[str, tuple[ImageMode, ...]]:
        """Outputs of this operator."""
        return {
            "output": ("L", "RGB"),
        }
