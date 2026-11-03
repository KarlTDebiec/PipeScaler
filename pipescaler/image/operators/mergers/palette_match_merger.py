#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Matches an image's color palette to that of a reference image."""

from __future__ import annotations

from logging import warning
from typing import Any

from PIL import Image

from pipescaler.common.validation import val_int
from pipescaler.image.core import PaletteMatchMode, UnsupportedImageModeError
from pipescaler.image.core.operators import ImageMerger
from pipescaler.image.core.typing import ImageMode
from pipescaler.image.core.validation import validate_image
from pipescaler.image.utilities import (
    LocalPaletteMatcher,
    PaletteMatcher,
    PaletteShaderMatcher,
)
from pipescaler.image.utilities.palette_shader_matcher import PaletteShaderError

__all__ = ["PaletteMatchMerger"]


class PaletteMatchMerger(ImageMerger):
    """Matches an image's color palette to that of a reference image.

    Local matching requires a target that is a uniform integer upscale of the
    reference, with a scale of at least 2 on both axes. Basic matching has no
    image-size restriction. Local neighborhood ranges use reference pixels.
    Both modes prefer the GPU, including Metal on macOS, and fall back to the CPU
    when the runtime is unavailable or shader execution fails.
    """

    def __init__(
        self,
        palette_match_mode: PaletteMatchMode = PaletteMatchMode.BASIC,
        local_range: int = 1,
        **kwargs: Any,
    ):
        """Validate configuration and initialize.

        Arguments:
            palette_match_mode: mode of palette matching to perform
            local_range: range of adjacent pixels from which to draw best-fit color;
              1 checks a 3x3 window, 2 checks a 5x5 window, etc.
            **kwargs: additional keyword arguments passed to ImageMerger
        Raises:
            ValueError: if the mode is invalid or the local range is not positive
        """
        super().__init__(**kwargs)

        self.palette_match_mode = PaletteMatchMode(palette_match_mode)
        self.local_range = val_int(local_range, min_value=1)

    def __call__(self, *input_images: Image.Image) -> Image.Image:
        """Merge images.

        Arguments:
            *input_images: input images
        Returns:
            merged output image
        Raises:
            UnsupportedImageModeError: if an image mode is unsupported
            ValueError: if the input count, sizes, or local geometry is unsupported
        """
        if len(input_images) != 2:
            raise ValueError(f"Expected 2 input images, received {len(input_images)}")
        ref_image = validate_image(input_images[0], self.inputs()["ref"])
        fit_image = validate_image(input_images[1], self.inputs()["fit"])
        if ref_image.mode != fit_image.mode:
            raise UnsupportedImageModeError(
                f"Image mode '{ref_image.mode}' of reference image does not match mode "
                f"'{fit_image.mode}' of fit image"
            )

        try:
            return PaletteShaderMatcher.run(
                ref_image,
                fit_image,
                self.local_range,
                palette_match_mode=self.palette_match_mode,
            )
        except PaletteShaderError as exc:
            warning(
                f"{self.__class__.__name__}: Shader path unavailable ('{exc}'); "
                "falling back to CPU palette matcher."
            )
        if self.palette_match_mode == PaletteMatchMode.BASIC:
            return PaletteMatcher.run(ref_image, fit_image)
        return LocalPaletteMatcher.run(ref_image, fit_image, self.local_range)

    def __repr__(self) -> str:
        """Representation.

        Returns:
            string representation of this object
        """
        return (
            f"{self.__class__.__name__}("
            f"palette_match_mode=PaletteMatchMode.{self.palette_match_mode.name}, "
            f"local_range={self.local_range!r})"
        )

    @classmethod
    def inputs(cls) -> dict[str, tuple[ImageMode, ...]]:
        """Inputs to this operator.

        Returns:
            mapping of input names to their supported image modes
        """
        return {
            "ref": ("L", "RGB"),
            "fit": ("L", "RGB"),
        }

    @classmethod
    def outputs(cls) -> dict[str, tuple[ImageMode, ...]]:
        """Outputs of this operator.

        Returns:
            mapping of output names to their supported image modes
        """
        return {
            "output": ("L", "RGB"),
        }
