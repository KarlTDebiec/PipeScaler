#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Upscales image using xbrz."""
from __future__ import annotations

from typing import Any, Union

import numpy as np
import xbrz
from PIL import Image

from pipescaler.common import validate_int
from pipescaler.core import Stage, validate_mode


class XbrzProcessor(Stage):
    """Upscales image using xbrz.

    See [xbrz](https://github.com/ioistired/xbrz.py).
    """

    def __init__(self, scale: int = 4, **kwargs: Any) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            scale: Factor by which to scale output image relative to input
            **kwargs: Additional keyword arguments
        """
        self.scale = validate_int(scale, 2, 6)

    def __call__(
        self, *input_images: Union[Image.Image, tuple[Image.Image, ...]]
    ) -> Union[Image.Image, tuple[Image.Image, ...]]:
        input_image, output_mode = validate_mode(
            input_images[0], self.inputs["input"], "RGBA"
        )
        return self.process(input_image, output_mode)

    def process(self, input_image: Image.Image, output_mode: str) -> Image.Image:
        output_image = xbrz.scale_pillow(input_image, self.scale)
        if output_mode == "RGB":
            output_image = Image.fromarray(np.array(output_image)[:, :, :3])
        elif output_mode == "LA":
            output_image = output_image.convert("LA")
        elif output_mode in ("1", "L"):
            output_image = Image.fromarray(np.array(output_image)[:, :, :3]).convert(
                "L"
            )

        return output_image

    @classmethod
    @property
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links."""
        return "Upscales image using [xbrz](https://github.com/ioistired/xbrz.py)."

    @classmethod
    @property
    def inputs(cls) -> dict[str, tuple[str, ...]]:
        return {
            "input": ("1", "L", "LA", "RGB", "RGBA"),
        }

    @classmethod
    @property
    def outputs(cls) -> dict[str, tuple[str, ...]]:
        return {
            "output": ("1", "L", "LA", "RGB", "RGBA"),
        }
