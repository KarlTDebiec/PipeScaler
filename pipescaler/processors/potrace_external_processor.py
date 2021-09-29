#!/usr/bin/env python
#   pipescaler/processors/potrace_external_processor.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
""""""
from __future__ import annotations

from argparse import ArgumentParser
from subprocess import PIPE, Popen
from typing import Any

from PIL import Image
from PIL.ImageOps import invert
from reportlab.graphics.renderPM import drawToFile
from svglib.svglib import svg2rlg

from pipescaler.common import temporary_filename, validate_float
from pipescaler.core import (
    Processor,
    UnsupportedImageModeError,
    remove_palette_from_image,
    validate_image,
)


class PotraceExternalProcessor(Processor):
    def __init__(
        self,
        invert: float = False,
        blacklevel: float = 0.3,
        alphamax: float = 1.34,
        opttolerance: float = 0.2,
        scale: float = 1.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

        self.invert = invert
        self.blacklevel = validate_float(blacklevel, min_value=0)
        self.alphamax = validate_float(alphamax, min_value=0)
        self.opttolerance = validate_float(opttolerance, min_value=0)
        self.scale = validate_float(scale, min_value=0)

    def process_file(self, infile: str, outfile: str):
        # Read image
        input_image, input_mode = validate_image(infile, ["L"])

        # Trace image
        with temporary_filename(".bmp") as bmpfile:
            with temporary_filename(".svg") as svgfile:
                with temporary_filename(".png") as pngfile:
                    # Convert to bmp
                    if self.invert:
                        invert(input_image).save(bmpfile)
                    else:
                        input_image.save(bmpfile)

                    # Trace
                    command = (
                        f"potrace {bmpfile}"
                        f" -b svg"
                        f" -k {self.blacklevel}"
                        f" -a {self.alphamax}"
                        f" -O {self.opttolerance}"
                        f" -o {svgfile}"
                    )
                    child = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
                    exitcode = child.wait(10)
                    if exitcode != 0:
                        out, err = child.communicate()
                        raise ValueError(
                            f"potrace subprocess failed;\n\n"
                            f"STDOUT\n"
                            f"{out.decode('utf8')}\n\n"
                            f"STDERR\n"
                            f"{err.decode('utf8')}"
                        )

                    # Scale
                    traced_drawing = svg2rlg(svgfile)
                    traced_drawing.scale(
                        (input_image.size[0] / traced_drawing.width) * self.scale,
                        (input_image.size[1] / traced_drawing.height) * self.scale,
                    )
                    traced_drawing.width = input_image.size[0] * self.scale
                    traced_drawing.height = input_image.size[1] * self.scale
                    drawToFile(traced_drawing, pngfile, fmt="png")

                    # Convert mode
                    output_image = Image.open(pngfile).convert("L")
                    if self.invert:
                        output_image = invert(output_image)

        # Write image
        output_image.save(outfile)

    @classmethod
    def construct_argparser(cls) -> ArgumentParser:
        """
        Constructs argument parser.

        Returns:
            parser (ArgumentParser): Argument parser
        """
        parser = super().construct_argparser(description=__doc__)

        parser.add_argument(
            "--invert",
            action="store_true",
            help="invert image before tracing, and revert afterwards",
        )
        parser.add_argument(
            "--blacklevel",
            default=0.3,
            type=cls.float_arg(min_value=0),
            help="black/white cutoff in input file (0.0-1.0, default: " "%(default)s)",
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
    PotraceExternalProcessor.main()
