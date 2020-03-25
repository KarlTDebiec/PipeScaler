#!python
# -*- coding: utf-8 -*-
#   lauhseuisin/processors/PotraceShadowProcessor.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
################################### MODULES ###################################
from __future__ import annotations

from argparse import ArgumentParser, ArgumentError
from os import remove, access, R_OK
from os.path import expandvars, splitext, isfile
from subprocess import Popen
import numpy as np
from typing import Any

from IPython import embed

from PIL import Image

from lauhseuisin.processors.Processor import Processor


################################### CLASSES ###################################
class PotraceShadowProcessor(Processor):

    def __init__(self, blacklevel: float = 0.3, alphamax: float = 1.34,
                 opttolerance: float = 0.2, scale: int = 4,
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.blacklevel = blacklevel
        self.alphamax = alphamax
        self.opttolerance = opttolerance
        self.scale = scale

        self.desc = f"potrace-{self.blacklevel:4.2f}-" \
                    f"{self.alphamax:4.2f}-{self.opttolerance:3.1f}-" \
                    f"{self.scale}"

    def process_file_in_pipeline(self, infile: str, outfile: str) -> None:
        self.process_file(infile, outfile, self.blacklevel, self.alphamax,
                          self.opttolerance, self.scale,
                          self.pipeline.verbosity)

    @classmethod
    def construct_argparser(cls) -> ArgumentParser:
        """
        Constructs argument parser

        Returns:
            parser (ArgumentParser): Argument parser
        """

        def infile_argument(value: str) -> str:
            if not isinstance(value, str):
                raise ArgumentError()

            value = expandvars(value)
            if not isfile(value):
                raise ArgumentError(f"infile '{value}' does not exist")
            elif not access(value, R_OK):
                raise ArgumentError(f"infile '{value}' cannot be read")

            return value

        parser = super().construct_argparser(description=__doc__)

        parser.add_argument(
            "-k", "--blacklevel",
            default=0.3,
            type=float,
            help="black/white cutoff in input file (default: 0.3)")
        parser.add_argument(
            "-a", "--alphamax",
            default=1.34,
            type=float,
            help="corner threshold parameter (default: 1.34)")
        parser.add_argument(
            "-O", "--opttolerance",
            default=0.2,
            type=float,
            help="curve optimization tolerance (default: 0.2)")
        parser.add_argument(
            "-s", "--scale",
            default=4,
            dest="scale",
            type=int,
            help="scale factor (default: 4)")

        return parser

    @classmethod
    def process_file(cls, infile: str, outfile: str, blacklevel: float,
                     alphamax: float, opttolerance: float, scale: int,
                     verbosity: int):
        # TODO: Use temporary files

        # Flatten image and convert to bmp; potrace does not accept png
        bmpfile = f"{splitext(infile)[0]}.bmp"
        input_image = Image.open(infile)
        canvas = Image.new("RGBA", input_image.size, (255, 255, 255))
        composite = Image.alpha_composite(canvas, input_image)
        point = composite.point(lambda p: p > 240 and 255)
        point.save(bmpfile)

        # Trace to svg
        svgfile = f"{splitext(outfile)[0]}.svg"
        command = f"potrace " \
                  f"{bmpfile} " \
                  f"-b svg " \
                  f"-k {blacklevel} " \
                  f"-a {alphamax} " \
                  f"-O {opttolerance} " \
                  f"-o {svgfile}"
        if verbosity >= 1:
            print(command)
        Popen(command, shell=True, close_fds=True).wait()

        # Rasterize svg to png and scale
        command = f"convert " \
                  f"-resize {scale * 100}% " \
                  f"{svgfile} " \
                  f"{outfile}"
        if verbosity >= 1:
            print(command)
        Popen(command, shell=True, close_fds=True).wait()

        # Convert back to shadow
        raster_image = Image.open(outfile).convert("L")
        output_data = np.zeros((raster_image.size[0], raster_image.size[1], 4))
        output_data[:,:,3] = (255 - np.array(raster_image))*0.666667
        output_image = Image.fromarray(output_data.astype(np.uint8))
        output_image.save(outfile)

        # Clean up
        remove(bmpfile)
        remove(svgfile)


#################################### MAIN #####################################
if __name__ == "__main__":
    PotraceShadowProcessor.main()
