#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Quantizes images with libimagequant without an external executable."""

from __future__ import annotations

import imagequant
from PIL import Image

from pipescaler.common.validation import val_float, val_int
from pipescaler.image.core import UnsupportedImageModeError
from pipescaler.image.core.operators import ImageProcessor
from pipescaler.image.core.typing import ImageMode

__all__ = ["ImagequantProcessor"]


class ImagequantProcessor(ImageProcessor):
    """Reduces an image to an RGBA palette using libimagequant.

    Returns the original image when the minimum quality cannot be met, for 16-bit
    grayscale inputs, or for grayscale inputs with an ICC profile that cannot
    describe an RGB palette. Successful quantization produces mode `P`, including
    palette transparency and source color metadata. PNG metadata encoding and
    file-size selection are handled by `pipescaler.image.quantization.quantize_png`.
    """

    def __init__(
        self,
        max_colors: int = 256,
        min_quality: int = 10,
        max_quality: int = 100,
        dithering_level: float = 0.0,
    ):
        """Validate and store quantization settings.

        Arguments:
            max_colors: maximum palette size, from 2 to 256
            min_quality: minimum acceptable quality, from 0 to 100
            max_quality: target quality, from min_quality to 100
            dithering_level: dithering strength, from 0 to 1; 0 disables dithering
        Raises:
            ValueError: if settings are out of range, non-finite, or inconsistent
        """
        super().__init__()
        self.max_colors = val_int(max_colors, min_value=2, max_value=256)
        """Maximum number of palette entries."""
        self.min_quality = val_int(min_quality, min_value=0, max_value=100)
        """Minimum acceptable quantization quality."""
        self.max_quality = val_int(max_quality, min_value=0, max_value=100)
        """Target quantization quality."""
        self.dithering_level = val_float(
            dithering_level, min_value=0, max_value=1, finite=True
        )
        """Dithering strength, with zero disabling dithering."""
        if self.min_quality > self.max_quality:
            raise ValueError("min_quality must not exceed max_quality")

    def __call__(self, input_image: Image.Image) -> Image.Image:
        """Quantize pixels while retaining source precision and color interpretation.

        Arguments:
            input_image: image to quantize; its pixels and metadata are not modified
        Returns:
            paletted image, or the original if quality, precision, or its grayscale
            ICC profile prevents quantization
        Raises:
            UnsupportedImageModeError: if the input mode is unsupported
            ValueError: if either image dimension is zero
            RuntimeError: if libimagequant fails for a reason other than low quality
        """
        if input_image.mode not in self.inputs()["input"]:
            raise UnsupportedImageModeError(
                f"Mode '{input_image.mode}' is not supported by {self}"
            )
        if input_image.width == 0 or input_image.height == 0:
            raise ValueError("Image dimensions must be nonzero")
        if input_image.mode == "I;16" or (
            input_image.mode in ("1", "L", "LA") and input_image.info.get("icc_profile")
        ):
            return input_image
        rgba_image = input_image.convert("RGBA")
        try:
            pixels, palette = imagequant.quantize_raw_rgba_bytes(
                rgba_image.tobytes(),
                rgba_image.width,
                rgba_image.height,
                max_colors=self.max_colors,
                min_quality=self.min_quality,
                max_quality=self.max_quality,
                dithering_level=self.dithering_level,
            )
        except RuntimeError as exc:
            if str(exc) == "Quality too low":
                return input_image
            raise

        palette = palette[: (max(pixels) + 1) * 4]
        output_image = Image.frombytes("P", input_image.size, pixels)
        output_image.info.update(
            {
                key: input_image.info[key]
                for key in ("icc_profile", "gamma", "chromaticity", "srgb")
                if key in input_image.info
            }
        )
        output_image.putpalette(
            [
                channel
                for start in range(0, len(palette), 4)
                for channel in palette[start : start + 3]
            ]
        )
        # Keep transparency explicit for Pillow and subsequent pipeline operators
        alpha = bytes(palette[3::4])
        if any(value < 255 for value in alpha):
            output_image.info["transparency"] = alpha
        return output_image

    def __repr__(self) -> str:
        """Return a reconstructible representation.

        Returns:
            string representation of this processor
        """
        return (
            f"{self.__class__.__name__}(max_colors={self.max_colors!r}, "
            f"min_quality={self.min_quality!r}, max_quality={self.max_quality!r}, "
            f"dithering_level={self.dithering_level!r})"
        )

    @classmethod
    def inputs(cls) -> dict[str, tuple[ImageMode, ...]]:
        """Describe supported input modes, including existing palettes.

        Returns:
            mapping of input names to supported image modes
        """
        return {"input": ("1", "L", "LA", "P", "RGB", "RGBA", "I;16")}

    @classmethod
    def outputs(cls) -> dict[str, tuple[ImageMode, ...]]:
        """Describe paletted output and modes retained on quality rejection.

        Returns:
            mapping of output names to possible image modes
        """
        return {"output": ("P", "1", "L", "LA", "RGB", "RGBA", "I;16")}
