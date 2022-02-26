#!/usr/bin/env python
#   pipescaler/processors/external/potrace_processor.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Traces image using Potrace and re-rasterizes, optionally resizing"""
from __future__ import annotations

from argparse import ArgumentParser
from inspect import cleandoc
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
from pipescaler.core import ExternalProcessor, validate_image


class PotraceProcessor(ExternalProcessor):
    """
    Traces image using [Potrace](http://potrace.sourceforge.net/) and re-rasterizes,
    optionally resizing
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
    def command_template(self):
        """String template with which to generate command"""
        command = (
            f"{validate_executable(self.executable, self.supported_platforms)}"
            " {bmpfile}"
            f" -b svg"
            f" -k {self.blacklevel}"
            f" -a {self.alphamax}"
            f" -O {self.opttolerance}"
            " -o {svgfile}"
        )

        return command

    @property
    def executable(self) -> str:
        """Name of executable"""
        return "potrace"

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
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """
        Construct argument parser

        Arguments:
            **kwargs: Additional keyword arguments

        Returns:
            parser: Argument parser
        """
        description = kwargs.pop(
            "description", cleandoc(cls.__doc__) if cls.__doc__ is not None else ""
        )
        parser = super().construct_argparser(description=description, **kwargs)

        parser.add_argument(
            "--invert",
            action="store_true",
            help="invert image before tracing, and revert afterwards",
        )
        parser.add_argument(
            "--blacklevel",
            default=0.3,
            type=cls.float_arg(min_value=0),
            help="black/white cutoff in input file (0.0-1.0, default: %(default)s)",
        )
        parser.add_argument(
            "--alphamax",
            default=1.34,
            type=cls.float_arg(min_value=0),
            help="corner threshold parameter (default: %(default)s)",
        )
        parser.add_argument(
            "--opttolerance",
            default=0.2,
            type=cls.float_arg(min_value=0),
            help="curve optimization tolerance (default: %(default)s)",
        )
        parser.add_argument(
            "--scale",
            default=1.0,
            type=cls.float_arg(min_value=0),
            help="curve optimization tolerance (default: %(default)s)",
        )

        return parser


if __name__ == "__main__":
    PotraceProcessor.main()
