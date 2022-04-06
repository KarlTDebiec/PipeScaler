#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Traces image using potrace and re-rasterizes, optionally resizing."""
from __future__ import annotations

from logging import debug
from typing import Any

from PIL import Image
from PIL.ImageOps import invert
from reportlab.graphics.renderPM import drawToFile
from svglib.svglib import svg2rlg

from pipescaler.common import (
    run_command,
    temporary_filename,
    validate_executable,
    validate_float,
)
from pipescaler.core import validate_image
from pipescaler.core.stages.processors import ExternalProcessor


class PotraceProcessor(ExternalProcessor):
    """Traces image using potrace and re-rasterizes, optionally resizing.

    See [Potrace](http://potrace.sourceforge.net/).
    """

    def __init__(
        self,
        invert: float = False,
        blacklevel: float = 0.3,
        alphamax: float = 1.34,
        opttolerance: float = 0.2,
        scale: float = 1.0,
        **kwargs: Any,
    ) -> None:
        """
        Validate and store static configuration

        Arguments:
            invert: Invert bitmap
            blacklevel: Black/white cutoff in input file
            alphamax: Corner threshold parameter
            opttolerance: Curve optimization tolerance
            scale: Factor by which to scale output image relative to input
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        self.invert = invert
        self.blacklevel = validate_float(blacklevel, min_value=0)
        self.alphamax = validate_float(alphamax, min_value=0)
        self.opttolerance = validate_float(opttolerance, min_value=0)
        self.scale = validate_float(scale, min_value=0)

    @property
    def command_template(self) -> str:
        """String template with which to generate command"""
        return (
            f"{validate_executable(self.executable, self.supported_platforms)}"
            " {bmpfile}"
            f" -b svg"
            f" -k {self.blacklevel}"
            f" -a {self.alphamax}"
            f" -O {self.opttolerance}"
            " -o {svgfile}"
        )

    def process(self, infile: str, outfile: str) -> None:
        """
        Read image from infile, process it, and save to outfile

        Arguments:
            infile: Input file path
            outfile: Output file path
        """
        input_image = validate_image(infile, ["1", "L"])
        if self.invert:
            input_image = invert(input_image)

        with temporary_filename(".bmp") as bmpfile:
            input_image.save(bmpfile)

            with temporary_filename(".svg") as svgfile:
                command = self.command_template.format(bmpfile=bmpfile, svgfile=svgfile)
                debug(f"{self}: {command}")
                run_command(command)

                with temporary_filename(".png") as pngfile:
                    traced_drawing = svg2rlg(svgfile)
                    traced_drawing.scale(
                        (input_image.size[0] / traced_drawing.width) * self.scale,
                        (input_image.size[1] / traced_drawing.height) * self.scale,
                    )
                    traced_drawing.width = input_image.size[0] * self.scale
                    traced_drawing.height = input_image.size[1] * self.scale
                    drawToFile(traced_drawing, pngfile, fmt="png")

                    output_image = Image.open(pngfile).convert("L")

        if self.invert:
            output_image = invert(output_image)
        output_image.save(outfile)

    @classmethod
    @property
    def executable(self) -> str:
        """Name of executable"""
        return "potrace"

    @classmethod
    @property
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links."""
        return (
            "Traces image using [Potrace](http://potrace.sourceforge.net/) and "
            "re-rasterizes,optionally resizing."
        )
