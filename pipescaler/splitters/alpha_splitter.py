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

from enum import Enum, auto
from typing import Any, List, Tuple, Union

import numpy as np
from PIL import Image

from pipescaler.common import validate_enum
from pipescaler.core import Splitter, fill_mask, is_monochrome


class AlphaMode(Enum):
    """Mode of output alpha image"""

    L = auto()
    L_OR_1 = auto()
    L_OR_1_FILL = auto()


class AlphaSplitter(Splitter):
    """Splits image with transparency into separate alpha and color images"""

    def __init__(
        self, alpha_mode: Union[AlphaMode, str] = AlphaMode.L, **kwargs: Any
    ) -> None:
        """
        Validate and store static configuration

        Arguments:
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        self.alpha_mode = validate_enum(alpha_mode, AlphaMode)

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

        if self.alpha_mode in (AlphaMode.L_OR_1, AlphaMode.L_OR_1_FILL):
            if is_monochrome(alpha_image):
                alpha_image = alpha_image.convert("1")
        if self.alpha_mode == AlphaMode.L_OR_1_FILL and alpha_image.mode == "1":
            color_image = fill_mask(color_image, alpha_image)

        return color_image, alpha_image
