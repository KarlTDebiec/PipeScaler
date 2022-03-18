#!/usr/bin/env python
#   pipescaler/mergers/palette_match_merger.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Matches an image's color palette to that of a reference image"""
from __future__ import annotations

from typing import Any, Dict, List, Union

from PIL import Image

from pipescaler.common import validate_enum
from pipescaler.core import Merger, PaletteMatchMode, UnsupportedImageModeError
from pipescaler.util import PaletteMatcher


class PaletteMatchMerger(Merger):
    """Matches an image's color palette to that of a reference image"""

    def __init__(
        self,
        palette_match_mode: Union[type(PaletteMatchMode), str] = PaletteMatchMode.BASIC,
        **kwargs: Any,
    ) -> None:
        """
        Validate and store static configuration

        Arguments:
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        self.palette_match_mode = validate_enum(palette_match_mode, PaletteMatchMode)
        self.palette_matcher = PaletteMatcher(self.palette_match_mode)

    @property
    def inlets(self) -> List[str]:
        """Inlets that flow into stage"""
        return ["reference", "fit"]

    @property
    def supported_input_modes(self) -> Dict[str, List[str]]:
        """Supported modes for input images"""
        return {
            "reference": ["L", "RGB"],
            "fit": ["L", "RGB"],
        }

    def merge(self, *input_images: Image.Image) -> Image.Image:
        """
        Merge images

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
