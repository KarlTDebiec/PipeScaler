#!python
#   lauhseuisin/processors/WaifuProcessor.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
################################### MODULES ###################################
from __future__ import annotations

from argparse import ArgumentParser
from os import remove
from os.path import expandvars
from subprocess import Popen
from tempfile import NamedTemporaryFile
from typing import Any, IO, Optional

from PIL import Image

from lauhseuisin.processors.Processor import Processor


################################### CLASSES ###################################
class WaifuProcessor(Processor):

    def __init__(self, imagetype: str = "a", scale: int = 2, denoise: int = 1,
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.imagetype = imagetype
        self.scale = scale
        self.denoise = denoise
        self.desc = f"waifu-{self.imagetype}-{self.scale}-{self.denoise}"

    def process_file_in_pipeline(self, infile: str, outfile: str) -> None:
        self.process_file(infile, outfile, self.imagetype, self.scale,
                          self.denoise, self.pipeline.verbosity)

    @classmethod
    def construct_argparser(cls) -> ArgumentParser:
        """
        Constructs argument parser

        Returns:
            parser (ArgumentParser): Argument parser
        """
        parser = super().construct_argparser(description=__doc__)

        parser.add_argument(
            "-t", "--type",
            default="a",
            dest="imagetype",
            type=str,
            help="image type - a for anime (default), p for photo")
        parser.add_argument(
            "-s", "--scale",
            default=2,
            dest="scale",
            type=int,
            help="scale factor (1 or 2)")
        parser.add_argument(
            "-n", "--noise",
            default=1,
            dest="denoise",
            type=int,
            help="denoise level (0-4)")

        return parser

    @classmethod
    def process_file(cls, infile: str, outfile: str, imagetype: str,
                     scale: int, denoise: int, verbosity: int):
        image = Image.open(infile)
        original_size = image.size

        # waifu needs images to be a minimum size; expand canvas if necessary
        tempfile: Optional[IO[bytes]] = None
        if original_size[0] < 200 or original_size[1] < 200:
            tempfile = NamedTemporaryFile(delete=False, suffix=".png")
            expanded_image = Image.new(
                image.mode, (max(200, original_size[0]),
                             max(200, original_size[1])))
            expanded_image.paste(
                image, (0, 0, original_size[0], original_size[1]))
            expanded_image.save(tempfile)
            tempfile.close()
            waifu_infile = tempfile.name
        else:
            waifu_infile = infile

        # Upscale
        command = f"waifu2x " \
                  f"-t {imagetype} " \
                  f"-s {scale} " \
                  f"-n {denoise} " \
                  f"-i {waifu_infile} " \
                  f"-o {outfile}"
        if verbosity >= 1:
            print(cls.get_indented_text(command))
        Popen(command, shell=True, close_fds=True).wait()

        # If canvas was expanded, crop image
        if tempfile is not None:
            Image.open(outfile).crop(
                (0, 0, original_size[0] * scale,
                 original_size[1] * scale)).save(outfile)
            remove(tempfile.name)


#################################### MAIN #####################################
if __name__ == "__main__":
    WaifuProcessor.main()
