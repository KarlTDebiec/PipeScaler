#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Matches an image's color palette to that of a reference image."""
from __future__ import annotations

from typing import Any, Union

from PIL import Image

from pipescaler.common import validate_enum
from pipescaler.core import PaletteMatchMode
from pipescaler.core.image import Merger, UnsupportedImageModeError, validate_image
from pipescaler.utilities import LocalPaletteMatcher, PaletteMatcher


class PaletteMatchMerger(Merger):
    """Matches an image's color palette to that of a reference image."""

    def __init__(
        self,
        palette_match_mode: Union[PaletteMatchMode, str] = PaletteMatchMode.BASIC,
        local_range: int = 1,
        **kwargs: Any,
    ) -> None:
        """Validate configuration and initialize.

        Arguments:
            palette_match_mode: Mode of palette matching to perform
            local_range: Range of adjacent pixels from which to draw best-fit color;
              1 checks a 3x3 window, 2 checks a 5x5 window, etc.
        """
        super().__init__(**kwargs)

        self.palette_match_mode = validate_enum(palette_match_mode, PaletteMatchMode)
        if self.palette_match_mode == PaletteMatchMode.BASIC:
            self.palette_matcher: Union[
                PaletteMatcher, LocalPaletteMatcher
            ] = PaletteMatcher()
        else:
            self.palette_matcher = LocalPaletteMatcher(local_range)

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

        output_image = self.palette_matcher.match_palette(ref_image, fit_image)

        return output_image

    def __repr__(self) -> str:
        """Representation."""
        return (
            f"{self.__class__.__name__}("
            f"palette_match_mode={self.palette_match_mode},"
            f"local_range={self.palette_matcher.local_range})"
        )

    @classmethod
    def inputs(cls) -> dict[str, tuple[str, ...]]:
        """Inputs to this operator."""
        return {
            "ref": ("L", "RGB"),
            "fit": ("L", "RGB"),
        }

    @classmethod
    def outputs(cls) -> dict[str, tuple[str, ...]]:
        """Outputs of this operator."""
        return {
            "output": ("L", "RGB"),
        }
