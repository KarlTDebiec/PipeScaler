#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Quantizes PNG files with metadata preservation and original-file fallback."""

from __future__ import annotations

from pathlib import Path
from shutil import copyfile
from struct import pack

from PIL import Image
from PIL.PngImagePlugin import PngInfo

from pipescaler.common.file import get_temp_file_path
from pipescaler.common.validation import val_input_path, val_output_path

from .operators.processors.imagequant_processor import ImagequantProcessor

__all__ = ["quantize_png"]


def quantize_png(
    input_path: Path,
    output_path: Path,
    *,
    processor: ImagequantProcessor | None = None,
    skip_if_larger: bool = True,
):
    """Quantize a static PNG and atomically publish the selected output.

    Retains original bytes when minimum quality cannot be met, the processor
    preserves input precision or its grayscale ICC profile, or the encoded result
    is not smaller and skip_if_larger is enabled. Successful quantization preserves
    ICC, gamma, chromaticity, and sRGB metadata. Input and output may be the same
    path. Failures leave existing output intact; its directory must already exist.

    This file callable can be passed directly to `ImageCheckpointManager.post_runner`.
    Use `functools.partial` to bind custom quantization or size-selection settings.

    Arguments:
        input_path: static PNG input file
        output_path: destination with a .png suffix
        processor: configured quantizer; defaults to ImagequantProcessor()
        skip_if_larger: whether to retain the original unless output is smaller
    Raises:
        ValueError: if the input is not a static PNG or output suffix is not .png
        OSError: if reading, encoding, or publishing the image fails
        RuntimeError: if quantization fails for a reason other than low quality
    """
    input_path = val_input_path(input_path)
    output_path = val_output_path(output_path, exist_ok=True, create=False)
    if output_path.suffix.lower() != ".png":
        raise ValueError("quantize_png output must have a .png suffix")
    if processor is None:
        processor = ImagequantProcessor()

    with get_temp_file_path(".png", parent_dir_path=output_path.parent) as temp_path:
        with Image.open(input_path) as input_image:
            if input_image.format != "PNG" or getattr(
                input_image, "is_animated", False
            ):
                raise ValueError("quantize_png input must be a static PNG")
            output_image = processor(input_image)
            if output_image is input_image:
                copyfile(input_path, temp_path)
            else:
                # Pillow requires explicit chunks for these color-space tags
                png_info = PngInfo()
                if "gamma" in output_image.info:
                    png_info.add(
                        b"gAMA", pack(">I", round(output_image.info["gamma"] * 100000))
                    )
                if "chromaticity" in output_image.info:
                    png_info.add(
                        b"cHRM",
                        pack(
                            ">8I",
                            *(
                                round(value * 100000)
                                for value in output_image.info["chromaticity"]
                            ),
                        ),
                    )
                if "srgb" in output_image.info:
                    png_info.add(b"sRGB", pack("B", output_image.info["srgb"]))
                output_image.save(
                    temp_path, format="PNG", optimize=True, pnginfo=png_info
                )
                if (
                    skip_if_larger
                    and temp_path.stat().st_size >= input_path.stat().st_size
                ):
                    copyfile(input_path, temp_path)
        temp_path.replace(output_path)
