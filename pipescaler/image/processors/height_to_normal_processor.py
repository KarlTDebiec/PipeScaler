#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Converts height map image to a normal map image."""
from __future__ import annotations

from typing import Any, Optional

from PIL import Image

from pipescaler.common import validate_float
from pipescaler.core.image import (
    Processor,
    generate_normal_map_from_height_map_image,
    smooth_image,
)
from pipescaler.core.validation import validate_mode


class HeightToNormalProcessor(Processor):
    """Converts height map image to a normal map image."""

    def __init__(self, sigma: Optional[float] = None, **kwargs: Any) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            sigma: Gaussian smoothing to apply to image
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        self.sigma = validate_float(sigma, min_value=0) if sigma is not None else None

    def __call__(self, input_image: Image.Image) -> Image.Image:
        input_image, _ = validate_mode(input_image, self.inputs["input"])
        if self.sigma is not None:
            input_image = smooth_image(input_image, self.sigma)
        output_image = generate_normal_map_from_height_map_image(input_image)

        return output_image

    @classmethod
    @property
    def inputs(cls) -> dict[str, tuple[str, ...]]:
        return {
            "input": ("L",),
        }

    @classmethod
    @property
    def outputs(cls) -> dict[str, tuple[str, ...]]:
        return {
            "output": ("RGB",),
        }
