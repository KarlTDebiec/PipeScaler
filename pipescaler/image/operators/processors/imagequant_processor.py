#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Quantizes images with libimagequant without an external executable."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from shutil import copyfile
from struct import pack

import imagequant
from PIL import Image
from PIL.PngImagePlugin import PngInfo

from pipescaler.common.file import get_temp_file_path
from pipescaler.common.validation import (
    val_float,
    val_input_path,
    val_int,
    val_output_path,
)
from pipescaler.image.core import UnsupportedImageModeError
from pipescaler.image.core.operators import ImageProcessor
from pipescaler.image.core.typing import ImageMode

__all__ = ["ImagequantProcessor"]


class ImagequantProcessor(ImageProcessor):
    """Reduces an image to an RGBA palette using libimagequant.

    Returns the original image when minimum quality cannot be met, a grayscale
    ICC profile cannot describe an RGB palette, or the encoded PNG is not smaller
    and skip_if_larger is enabled. Successful quantization produces mode `P`,
    including palette transparency and source color metadata.

    Image calls compare optimized PNG encodings in memory. `process_file` compares
    against the original file size and preserves original bytes on fallback.
    """

    def __init__(
        self,
        max_colors: int = 256,
        min_quality: int = 10,
        max_quality: int = 100,
        dithering_level: float = 0.0,
        *,
        skip_if_larger: bool = True,
    ):
        """Validate and store quantization settings.

        Arguments:
            max_colors: maximum palette size, from 2 to 256
            min_quality: minimum acceptable quality, from 0 to 100
            max_quality: target quality, from min_quality to 100
            dithering_level: dithering strength, from 0 to 1; 0 disables dithering
            skip_if_larger: whether to retain the original unless its PNG is smaller
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
        self.skip_if_larger = skip_if_larger
        """Whether to retain the original when its PNG encoding is no larger."""
        if self.min_quality > self.max_quality:
            raise ValueError("min_quality must not exceed max_quality")

    def __call__(self, input_image: Image.Image) -> Image.Image:
        """Quantize an image and select it by encoded PNG size when configured.

        Arguments:
            input_image: image to quantize; its pixels and metadata are not modified
        Returns:
            paletted image, or the original if quality, its grayscale ICC profile,
            or encoded PNG size prevents quantization
        Raises:
            UnsupportedImageModeError: if the input mode is unsupported
            ValueError: if either image dimension is zero
            OSError: if PNG encoding fails during size comparison
            RuntimeError: if libimagequant fails for a reason other than low quality
        """
        output_image = self._quantize(input_image)
        if output_image is input_image:
            return input_image
        if self.skip_if_larger and len(self._encode_png(output_image)) >= len(
            self._encode_png(input_image)
        ):
            return input_image
        return output_image

    def __repr__(self) -> str:
        """Return a reconstructible representation.

        Returns:
            string representation of this processor
        """
        return (
            f"{self.__class__.__name__}(max_colors={self.max_colors!r}, "
            f"min_quality={self.min_quality!r}, max_quality={self.max_quality!r}, "
            f"dithering_level={self.dithering_level!r}, "
            f"skip_if_larger={self.skip_if_larger!r})"
        )

    def process_file(self, input_path: Path, output_path: Path):
        """Quantize a static PNG and atomically publish the selected output.

        Retains exact input bytes on quality or size fallback, for 16-bit grayscale
        inputs, and for ICC-profiled grayscale inputs. Input and output may be the
        same path. The output directory must already exist. This bound method can
        be passed to `ImageCheckpointManager.post_runner`.

        Arguments:
            input_path: static PNG input file
            output_path: destination with a .png suffix
        Raises:
            ValueError: if the input is not a static PNG or output suffix is not .png
            OSError: if reading, encoding, or publishing the image fails
            RuntimeError: if quantization fails for a reason other than low quality
        """
        input_path = val_input_path(input_path)
        output_path = val_output_path(output_path, exist_ok=True, create=False)
        if output_path.suffix.lower() != ".png":
            raise ValueError("Output must have a .png suffix")

        with get_temp_file_path(
            ".png", parent_dir_path=output_path.parent
        ) as temp_path:
            with Image.open(input_path) as input_image:
                if input_image.format != "PNG" or getattr(
                    input_image, "is_animated", False
                ):
                    raise ValueError("Input must be a static PNG")
                if input_image.mode == "I;16":
                    output_image = input_image
                else:
                    output_image = self._quantize(input_image)
                if output_image is input_image:
                    copyfile(input_path, temp_path)
                else:
                    encoded = self._encode_png(output_image)
                    if (
                        self.skip_if_larger
                        and len(encoded) >= input_path.stat().st_size
                    ):
                        copyfile(input_path, temp_path)
                    else:
                        temp_path.write_bytes(encoded)
            temp_path.replace(output_path)

    @classmethod
    def inputs(cls) -> dict[str, tuple[ImageMode, ...]]:
        """Describe supported input modes, including existing palettes.

        Returns:
            mapping of input names to supported image modes
        """
        return {"input": ("1", "L", "LA", "P", "RGB", "RGBA")}

    @classmethod
    def outputs(cls) -> dict[str, tuple[ImageMode, ...]]:
        """Describe paletted output and modes retained on quality or size rejection.

        Returns:
            mapping of output names to possible image modes
        """
        return {"output": ("P", "1", "L", "LA", "RGB", "RGBA")}

    def _quantize(self, input_image: Image.Image) -> Image.Image:
        """Generate a palette independently of image or file size selection.

        Arguments:
            input_image: image whose pixels and color metadata are to be quantized
        Returns:
            paletted image, or the original on quality or grayscale-profile fallback
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
        if input_image.mode in ("1", "L", "LA") and input_image.info.get("icc_profile"):
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

    @staticmethod
    def _encode_png(image: Image.Image) -> bytes:
        """Encode an optimized PNG with its color-space and transparency metadata.

        Arguments:
            image: image to encode without modifying its pixels or metadata
        Returns:
            encoded PNG bytes
        Raises:
            OSError: if PNG encoding fails
        """
        png_info = PngInfo()
        if "gamma" in image.info:
            png_info.add(b"gAMA", pack(">I", round(image.info["gamma"] * 100000)))
        if "chromaticity" in image.info:
            png_info.add(
                b"cHRM",
                pack(
                    ">8I",
                    *(round(value * 100000) for value in image.info["chromaticity"]),
                ),
            )
        if "srgb" in image.info:
            png_info.add(b"sRGB", pack("B", image.info["srgb"]))
        with BytesIO() as buffer:
            image.save(buffer, format="PNG", optimize=True, pnginfo=png_info)
            return buffer.getvalue()
