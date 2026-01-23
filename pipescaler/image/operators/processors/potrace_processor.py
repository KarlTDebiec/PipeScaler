#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Traces image using potrace and re-rasterizes, optionally resizing."""

from __future__ import annotations

from PIL import Image, ImageOps
from reportlab.graphics.renderPM import drawToFile
from svglib.svglib import svg2rlg

from pipescaler.common.file import get_temp_file_path
from pipescaler.common.validation import val_float
from pipescaler.image.core.operators import ImageProcessor
from pipescaler.image.core.typing import ImageMode
from pipescaler.image.core.validation import validate_image_and_convert_mode
from pipescaler.image.runners import PotraceRunner


class PotraceProcessor(ImageProcessor):
    """Traces image using potrace and re-rasterizes, optionally resizing.

    See [Potrace](http://potrace.sourceforge.net/).
    """

    def __init__(
        self,
        arguments: str = "-b svg -k 0.3 -a 1.34 -O 0.2",
        invert: bool = False,
        scale: float = 1.0,
    ):
        """Initialize.

        Arguments:
            arguments: Command-line arguments to pass to potrace
            invert: Whether to invert image before tracing
            scale: Scale of re-rasterized output image relative to input
        """
        super().__init__()

        self.potrace_runner = PotraceRunner(arguments)
        self.invert = invert
        self.scale = val_float(scale, min_value=0)

    def __call__(self, input_image: Image.Image) -> Image.Image:
        """Process an image.

        Arguments:
            input_image: Input image
        Returns:
            Processed output image
        """
        input_image, _ = validate_image_and_convert_mode(
            input_image, self.inputs()["input"], "L"
        )
        if self.invert:
            input_image = ImageOps.invert(input_image)

        with get_temp_file_path(".bmp") as temp_bmp_path:
            input_image.save(temp_bmp_path)

            with get_temp_file_path(".svg") as temp_svg_path:
                self.potrace_runner.run(temp_bmp_path, temp_svg_path)
                traced_drawing = svg2rlg(temp_svg_path)
                if not traced_drawing:
                    raise ValueError("No drawing found in SVG")
                traced_drawing.scale(
                    (input_image.size[0] / traced_drawing.width) * self.scale,
                    (input_image.size[1] / traced_drawing.height) * self.scale,
                )
                traced_drawing.width = int(input_image.size[0] * self.scale)
                traced_drawing.height = int(input_image.size[1] * self.scale)

                with get_temp_file_path(".png") as temp_png_path:
                    drawToFile(traced_drawing, temp_png_path, fmt="png")  # pyright: ignore[reportArgumentType]
                    output_image = Image.open(temp_png_path).convert("L")

        if self.invert:
            output_image = ImageOps.invert(output_image)

        return output_image

    def __repr__(self) -> str:
        """Representation."""
        return (
            f"{self.__class__.__name__}("
            f"arguments={self.potrace_runner.arguments!r}, "
            f"invert={self.invert!r}, "
            f"scale={self.scale!r})"
        )

    @classmethod
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links."""
        return (
            "Traces image using [Potrace](http://potrace.sourceforge.net/) and "
            "re-rasterizes, optionally resizing."
        )

    @classmethod
    def inputs(cls) -> dict[str, tuple[ImageMode, ...]]:
        """Inputs to this operator."""
        return {
            "input": ("1", "L"),
        }

    @classmethod
    def outputs(cls) -> dict[str, tuple[ImageMode, ...]]:
        """Outputs of this operator."""
        return {
            "output": ("1",),
        }
