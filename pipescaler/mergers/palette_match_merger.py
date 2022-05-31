#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Matches an image's color palette to that of a reference image."""
from __future__ import annotations

from typing import Any, Union

from PIL import Image

from pipescaler.common import validate_enum
from pipescaler.core import PaletteMatchMode, UnsupportedImageModeError
from pipescaler.core.stages import Merger
from pipescaler.utilities import LocalPaletteMatcher, PaletteMatcher


class PaletteMatchMerger(Merger):
    """Matches an image's color palette to that of a reference image."""

    def __init__(
        self,
        palette_match_mode: Union[type(PaletteMatchMode), str] = PaletteMatchMode.BASIC,
        **kwargs: Any,
    ) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            palette_match_mode: Mode of palette matching to perform
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        self.palette_match_mode = validate_enum(palette_match_mode, PaletteMatchMode)
        if self.palette_match_mode == PaletteMatchMode.BASIC:
            self.palette_matcher = PaletteMatcher()
        else:
            self.palette_matcher = LocalPaletteMatcher()

    def merge(self, *input_images: Image.Image) -> Image.Image:
        """Merge images.

        Arguments:
            *input_images: Input images to merge
        Returns:
            Merged output image
        """
        ref_image, fit_image = input_images
        if ref_image.mode != fit_image.mode:
            raise UnsupportedImageModeError(
                f"Image mode '{ref_image.mode}' of reference image does not match mode "
                f"'{fit_image.mode}' of fit image"
            )

        output_image = self.palette_matcher.match_palette(ref_image, fit_image)

        return output_image

    @property
    def inlets(self) -> list[str]:
        """Inlets that flow into stage."""
        return ["reference", "fit"]

    @classmethod
    @property
    def supported_input_modes(self) -> dict[str, list[str]]:
        """Supported modes for input images."""
        return {
            "reference": ["L", "RGB"],
            "fit": ["L", "RGB"],
        }
