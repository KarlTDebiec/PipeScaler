#!/usr/bin/env python
#   pipescaler/splitter/alpha_splitter.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Splits image with transparency into separate alpha and color images"""
from __future__ import annotations

from typing import Any, List, Optional, Tuple, Union

import numpy as np
from PIL import Image

from pipescaler.common import ArgumentConflictError, validate_enum
from pipescaler.core import AlphaMode, FillMode, Splitter, is_monochrome
from pipescaler.util import MaskFiller


class AlphaSplitter(Splitter):
    """Splits image with transparency into separate alpha and color images"""

    def __init__(
        self,
        alpha_mode: Union[type(AlphaMode), str] = AlphaMode.L,
        fill_mode: Optional[Union[type(FillMode), str]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Validate and store static configuration

        Arguments:
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        self.alpha_mode = validate_enum(alpha_mode, AlphaMode)
        self.fill_mode = None
        if fill_mode is not None:
            if self.alpha_mode == AlphaMode.L:
                raise ArgumentConflictError()
            self.fill_mode = validate_enum(fill_mode, FillMode)
            self.mask_filler = MaskFiller(fill_mode=self.fill_mode)

    @property
    def outlets(self) -> List[str]:
        """Outlets that flow out of stage"""
        return ["color", "alpha"]

    @property
    def supported_input_modes(self) -> List[str]:
        """Supported modes for input image"""
        return ["LA", "RGBA"]

    def split(self, input_image: Image.Image) -> Tuple[Image.Image, ...]:
        """
        Split an image

        Arguments:
            input_image: Input image to split
        Returns:
            Split output images
        """
        # noinspection PyTypeChecker
        input_array = np.array(input_image)
        color_array = np.squeeze(input_array[:, :, :-1])
        alpha_array = input_array[:, :, -1]

        color_image = Image.fromarray(color_array)
        alpha_image = Image.fromarray(alpha_array)

        if self.alpha_mode == AlphaMode.L_OR_1 and is_monochrome(alpha_image):
            alpha_image = alpha_image.convert("1")
        if self.fill_mode is not None and alpha_image.mode == "1":
            color_image = self.mask_filler.fill(color_image, alpha_image)

        return color_image, alpha_image
