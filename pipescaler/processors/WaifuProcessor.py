#!/usr/bin/env python
#   pipescaler/processors/WaifuProcessor.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Processes an image using waifu.

Requires the macOS version of waifu2x (https://github.com/imxieyi/waifu2x-mac)
in the executor's path.

Provides two improvements over running waifu2x directly:
1. If image is below waifu2x's minimum size, expands canvas.
2. Eliminates edge effects by reflecting image around edges.
"""
################################### MODULES ###################################
from __future__ import annotations

from argparse import ArgumentParser
from os import remove
from subprocess import Popen
from tempfile import NamedTemporaryFile
from typing import Any

from PIL import Image

from pipescaler.processors.Processor import Processor


################################### CLASSES ###################################
class WaifuProcessor(Processor):

    # region Builtins

    def __init__(self, imagetype: str = "a", scale: int = 2, denoise: int = 1,
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.imagetype = imagetype
        self.scale = scale
        self.denoise = denoise

    # endregion

    # region Properties

    @property
    def desc(self) -> str:
        """str: Description"""
        if not hasattr(self, "_desc"):
            return f"waifu-{self.imagetype}-{self.scale}-{self.denoise}"
        return self._desc

    # endregion

    # region Methods

    def process_file_in_pipeline(self, infile: str, outfile: str) -> None:
        self.process_file(infile, outfile, self.pipeline.verbosity,
                          imagetype=self.imagetype, scale=self.scale,
                          denoise=self.denoise)

    # endregion

    # region Class Methods

    @classmethod
    def construct_argparser(cls) -> ArgumentParser:
        """
        Constructs argument parser

        Returns:
            parser (ArgumentParser): Argument parser
        """
        parser = super().construct_argparser(description=__doc__)

        parser.add_argument(
            "--type",
            default="a",
            dest="imagetype",
            type=str,
            help="image type - a for anime, p for photo, (default: "
                 "%(default)s)")
        parser.add_argument(
            "--scale",
            default=2,
            dest="scale",
            type=int,
            help="scale factor (1 or 2, default: %(default)s)")
        parser.add_argument(
            "--denoise",
            default=1,
            dest="denoise",
            type=int,
            help="denoise level (0-4, default: %(default)s)")

        return parser

    @classmethod
    def process_file(cls, infile: str, outfile: str, verbosity: int = 1,
                     **kwargs: Any) -> None:
        imagetype = kwargs.get("imagetype")
        scale = kwargs.get("scale")
        denoise = kwargs.get("denoise")

        # Prepare temporary image with reflections and minimum size of 200x200
        image = Image.open(infile)
        w, h = image.size
        transposed_h = image.transpose(Image.FLIP_LEFT_RIGHT)
        transposed_v = image.transpose(Image.FLIP_TOP_BOTTOM)
        transposed_hv = transposed_h.transpose(Image.FLIP_TOP_BOTTOM)
        reflected = Image.new(
            image.mode, (max(200, int(w * 1.5)), max(200, int(h * 1.5))))
        x = reflected.size[0] // 2
        y = reflected.size[1] // 2
        reflected.paste(image, (x - w // 2, y - h // 2))
        reflected.paste(transposed_h, (x + w // 2, y - h // 2))
        reflected.paste(transposed_h, (x - w - w // 2, y - h // 2))
        reflected.paste(transposed_v, (x - w // 2, y - h - h // 2))
        reflected.paste(transposed_v, (x - w // 2, y + h // 2))
        reflected.paste(transposed_hv, (x + w // 2, y - h - h // 2))
        reflected.paste(transposed_hv, (x - w - w // 2, y - h - h // 2))
        reflected.paste(transposed_hv, (x - w - w // 2, y + h // 2))
        reflected.paste(transposed_hv, (x + w // 2, y + h // 2))
        tempfile = NamedTemporaryFile(delete=False, suffix=".png")
        reflected.save(tempfile)
        tempfile.close()

        # Process using waifu
        command = f"waifu2x " \
                  f"-t {imagetype} " \
                  f"-s {scale} " \
                  f"-n {denoise} " \
                  f"-i {tempfile.name} " \
                  f"-o {outfile}"
        if verbosity >= 1:
            print(command)
        Popen(command, shell=True, close_fds=True).wait()

        # Load processed image and crop back to original content
        reflected = Image.open(outfile).crop(
            ((x - w // 2) * scale,
             (y - h // 2) * scale,
             (x + w // 2) * scale,
             (y + h // 2) * scale))
        remove(tempfile.name)
        reflected.save(outfile)

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    WaifuProcessor.main()
