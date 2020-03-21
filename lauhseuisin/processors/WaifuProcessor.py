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
                 executable: str = "waifu", **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.imagetype = imagetype
        self.scale = scale
        self.denoise = denoise
        self.executable = expandvars(executable)
        self.desc = f"waifu-{self.imagetype}-{self.scale}-{self.denoise}"

    def process_file(self, infile: str, outfile: str) -> None:
        image = Image.open(infile)
        original_size = image.size

        # waifu needs images to be a minimum size; expand canvas if necessary
        tempfile: Optional[IO[bytes]] = None
        if original_size[0] < 200 or original_size[1] < 200:
            if self.pipeline.verbosity >= 1:
                print("creating temporary file")
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
        command = f"{self.executable} " \
                  f"-t {self.imagetype} " \
                  f"-s {self.scale} " \
                  f"-n {self.denoise} " \
                  f"-i {waifu_infile} " \
                  f"-o {outfile}"
        if self.pipeline.verbosity >= 1:
            print(command)
        Popen(command, shell=True, close_fds=True).wait()

        # If canvas was expanded, crop image
        if tempfile is not None:
            Image.open(outfile).crop(
                (0, 0, original_size[0] * self.scale,
                 original_size[1] * self.scale)).save(outfile)
            if self.pipeline.verbosity >= 1:
                print("removing temporary file")
            remove(tempfile.name)
