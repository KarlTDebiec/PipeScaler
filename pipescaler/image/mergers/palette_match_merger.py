#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Matches an image's color palette to that of a reference image."""
from __future__ import annotations

from typing import Any, Union

from PIL import Image

from pipescaler.common import validate_enum
from pipescaler.core.enums import PaletteMatchMode
from pipescaler.core.exceptions import UnsupportedImageModeError
from pipescaler.core.image import Merger
from pipescaler.core.validation import validate_mode
from pipescaler.utilities import LocalPaletteMatcher, PaletteMatcher


class PaletteMatchMerger(Merger):
    """Matches an image's color palette to that of a reference image."""

    def __init__(
        self,
        palette_match_mode: Union[type(PaletteMatchMode), str] = PaletteMatchMode.BASIC,
        local_range: int = 1,
        **kwargs: Any,
    ) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            palette_match_mode: Mode of palette matching to perform
        """
        super().__init__(**kwargs)

        self.palette_match_mode = validate_enum(palette_match_mode, PaletteMatchMode)
        if self.palette_match_mode == PaletteMatchMode.BASIC:
            self.palette_matcher = PaletteMatcher()
        else:
            self.palette_matcher = LocalPaletteMatcher(local_range)

    def __call__(self, *input_images: Image.Image) -> Image.Image:
        ref_image, _ = validate_mode(input_images[0], self.inputs["ref"])
        fit_image, _ = validate_mode(input_images[1], self.inputs["fit"])
        if ref_image.mode != fit_image.mode:
            raise UnsupportedImageModeError(
                f"Image mode '{ref_image.mode}' of reference image does not match mode "
                f"'{fit_image.mode}' of fit image"
            )

        output_image = self.palette_matcher.match_palette(ref_image, fit_image)

        return output_image

    @classmethod
    @property
    def inputs(cls) -> dict[str, tuple[str, ...]]:
        return {
            "ref": ("L", "RGB"),
            "fit": ("L", "RGB"),
        }

    @classmethod
    @property
    def outputs(cls) -> dict[str, tuple[str, ...]]:
        return {
            "output": ("L", "RGB"),
        }
