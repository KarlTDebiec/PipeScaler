#!python
#   lauhseuisin/processors/JointWaifuPixelmatorTransparentProcessor.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
################################### MODULES ###################################
from __future__ import annotations

from os import remove
from os.path import basename, expandvars
from shutil import copyfile
from subprocess import Popen
from tempfile import NamedTemporaryFile
from typing import Any, IO, Optional

import numpy as np
from PIL import Image

from lauhseuisin.processors.Processor import Processor


################################### CLASSES ###################################
class WaifuPixelmator2xTransparentProcessor(Processor):

    def __init__(self, workflow: str, imagetype: str = "a", denoise: str = 1,
                 waifu_executable: str = "waifu",
                 automator_executable: str = "automator",
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.imagetype = imagetype
        self.scale = 2
        self.denoise = denoise
        self.workflow = expandvars(workflow)
        self.waifu_executable = expandvars(waifu_executable)
        self.automator_executable = expandvars(automator_executable)
        self.desc = f"waifupixelmator2x-" \
                    f"{self.imagetype}-{self.scale}-{self.denoise}-" \
                    f"{basename(self.workflow).rstrip('.workflow')}"

    def process_file(self, infile: str, outfile: str) -> None:

        # Waifu 2X
        image = Image.open(infile)
        original_size = image.size
        tempfile: Optional[IO[bytes]] = None
        waifu_outfile = NamedTemporaryFile(delete=False, suffix=".png")
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
        command = f"{self.waifu_executable} " \
                  f"-t {self.imagetype} " \
                  f"-s {self.scale} " \
                  f"-n {self.denoise} " \
                  f"-i {waifu_infile} " \
                  f"-o {waifu_outfile.name}"
        if self.pipeline.verbosity >= 1:
            print(self.get_indented_text(command))
        Popen(command, shell=True, close_fds=True).wait()
        if tempfile is not None:
            Image.open(waifu_outfile.name).crop(
                (0, 0, original_size[0] * self.scale,
                 original_size[1] * self.scale)).save(waifu_outfile.name)
            remove(tempfile.name)
        waifu_2x_image = Image.open(waifu_outfile.name)
        remove(waifu_outfile.name)

        # Pixelmator 3X
        pixelmator_tempfile = NamedTemporaryFile(delete=False, suffix=".png")
        copyfile(infile, pixelmator_tempfile.name)
        command = f"{self.automator_executable} " \
                  f"-i {pixelmator_tempfile.name} " \
                  f"{self.workflow}"
        if self.pipeline.verbosity >= 1:
            print(self.get_indented_text(command))
        Popen(command, shell=True, close_fds=True).wait()
        pixelmator_3x_image = Image.open(pixelmator_tempfile.name)
        remove(pixelmator_tempfile.name)

        # Scale Pixelmator down to 2X
        pixelmator_2x_image = pixelmator_3x_image.resize((
            int(np.round(pixelmator_3x_image.size[0] * 0.66667)),
            int(np.round(pixelmator_3x_image.size[1] * 0.66667))),
            resample=Image.LANCZOS)

        # Paste waifu on top of pixelmator and set alpha to that of pixelmator
        merged_image = Image.new("RGBA", pixelmator_2x_image.size)
        merged_image = Image.alpha_composite(merged_image, pixelmator_2x_image)
        merged_image = Image.alpha_composite(merged_image, waifu_2x_image)
        merged_data = np.array(merged_image)
        merged_data[:, :, 3] = np.array(pixelmator_2x_image)[:, :, 3]
        final_image = Image.fromarray(merged_data)

        # Save final image
        final_image.save(outfile)


#################################### MAIN #####################################
if __name__ == "__main__":
    LauhSeuiSin.main()
