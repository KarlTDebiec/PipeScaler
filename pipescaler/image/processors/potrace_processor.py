#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Traces image using potrace and re-rasterizes, optionally resizing."""
from __future__ import annotations

from PIL import Image
from PIL.ImageOps import invert
from reportlab.graphics.renderPM import drawToFile
from svglib.svglib import svg2rlg

from pipescaler.common import temporary_filename, validate_float
from pipescaler.core.image import Processor
from pipescaler.core.validation import validate_mode
from pipescaler.runners import PotraceRunner


class PotraceProcessor(Processor):
    """Traces image using potrace and re-rasterizes, optionally resizing.

    See [Potrace](http://potrace.sourceforge.net/).
    """

    def __init__(
        self,
        arguments: str = "-b svg -k 0.3 -a 1.34 -O 0.2",
        invert: bool = False,
        scale: float = 1.0,
    ) -> None:
        """Validate and store configuration and initialize.

        Args:
            arguments: Command-line arguments to pass to potrace
            invert: Whether to invert image before tracing
            scale: Scale of re-rasterized output image relative to input
        """
        self.potrace_runner = PotraceRunner(arguments)
        self.invert = invert
        self.scale = validate_float(scale, min_value=0)

    def __call__(self, input_image: Image.Image) -> Image.Image:
        """Process an image.

        Args:
            input_image: Input image
        Returns:
            Processed output image
        """
        input_image, output_mode = validate_mode(input_image, self.inputs["input"], "L")
        if self.invert:
            input_image = invert(input_image)

        with temporary_filename(".bmp") as temp_bmp_file:
            input_image.save(temp_bmp_file)

            with temporary_filename(".svg") as temp_svg_file:
                self.potrace_runner.run(temp_bmp_file, temp_svg_file)
                traced_drawing = svg2rlg(temp_svg_file)
                traced_drawing.scale(
                    (input_image.size[0] / traced_drawing.width) * self.scale,
                    (input_image.size[1] / traced_drawing.height) * self.scale,
                )
                traced_drawing.width = input_image.size[0] * self.scale
                traced_drawing.height = input_image.size[1] * self.scale

                with temporary_filename(".png") as temp_png_file:
                    drawToFile(traced_drawing, temp_png_file, fmt="png")
                    output_image = Image.open(temp_png_file).convert("L")

        if self.invert:
            output_image = invert(output_image)

        return output_image

    @classmethod
    @property
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links."""
        return (
            "Traces image using [Potrace](http://potrace.sourceforge.net/) and"
            " re-rasterizes, optionally resizing."
        )

    @classmethod
    @property
    def inputs(cls) -> dict[str, tuple[str, ...]]:
        """Inputs to this operator."""
        return {
            "input": ("1", "L"),
        }

    @classmethod
    @property
    def outputs(cls) -> dict[str, tuple[str, ...]]:
        """Outputs of this operator."""
        return {
            "output": ("1",),
        }
