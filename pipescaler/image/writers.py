#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Writes quantized PNGs with original-file fallback."""

from __future__ import annotations

from pathlib import Path
from shutil import copyfile
from struct import pack

from PIL import Image
from PIL.PngImagePlugin import PngInfo

from pipescaler.common.file import get_temp_file_path
from pipescaler.common.validation import val_input_path, val_output_path

from .operators.processors.imagequant_processor import ImagequantProcessor

__all__ = ["ImagequantWriter"]


class ImagequantWriter:
    """Quantizes static PNG files and atomically writes the selected output.

    Preserves the original file bytes if minimum quality cannot be met or, by
    default, the encoded result is not smaller. Retains 16-bit grayscale and
    ICC-profiled grayscale inputs unchanged. Successful quantization preserves
    ICC, gamma, chromaticity, and sRGB metadata. This file callable can be passed
    to `ImageCheckpointManager.post_runner` without an external executable.
    """

    def __init__(
        self,
        processor: ImagequantProcessor | None = None,
        *,
        skip_if_larger: bool = True,
    ):
        """Store quantization and output-selection settings.

        Arguments:
            processor: configured quantizer; defaults to ImagequantProcessor()
            skip_if_larger: whether to retain the original unless output is smaller
        """
        if processor is None:
            processor = ImagequantProcessor()
        self.processor = processor
        """In-memory quantizer used to prepare the output."""
        self.skip_if_larger = skip_if_larger
        """Whether to retain original bytes when quantization does not reduce size."""

    def __call__(self, input_path: Path, output_path: Path):
        """Quantize a PNG and publish it, retaining original bytes when appropriate.

        Input and output may be the same path. Failures leave any existing output
        intact. The output directory must already exist.

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
            raise ValueError("ImagequantWriter output must have a .png suffix")

        with get_temp_file_path(
            ".png", parent_dir_path=output_path.parent
        ) as temp_path:
            with Image.open(input_path) as input_image:
                if input_image.format != "PNG" or getattr(
                    input_image, "is_animated", False
                ):
                    raise ValueError("ImagequantWriter input must be a static PNG")
                output_image = self.processor(input_image)
                if output_image is input_image:
                    copyfile(input_path, temp_path)
                else:
                    # Pillow requires explicit chunks for these color-space tags
                    png_info = PngInfo()
                    if "gamma" in output_image.info:
                        png_info.add(
                            b"gAMA",
                            pack(">I", round(output_image.info["gamma"] * 100000)),
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
                        self.skip_if_larger
                        and temp_path.stat().st_size >= input_path.stat().st_size
                    ):
                        copyfile(input_path, temp_path)
            temp_path.replace(output_path)

    def __repr__(self) -> str:
        """Return a reconstructible representation.

        Returns:
            string representation of this writer
        """
        return (
            f"{self.__class__.__name__}(processor={self.processor!r}, "
            f"skip_if_larger={self.skip_if_larger!r})"
        )
