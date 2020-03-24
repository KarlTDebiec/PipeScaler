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

from argparse import ArgumentError, ArgumentParser
from os import R_OK, access, remove
from os.path import basename, expandvars, isfile
from shutil import copyfile
from subprocess import Popen
from tempfile import NamedTemporaryFile
from typing import Any, IO, Optional

import numpy as np
from PIL import Image

from lauhseuisin.processors.Processor import Processor


################################### CLASSES ###################################
class WaifuPixelmator2xTransparentProcessor(Processor):

    def __init__(self, workflow: str, waifu_executable: str = "waifu",
                 imagetype: str = "a", denoise: str = 1,
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

    def process_file_in_pipeline(self, infile: str, outfile: str) -> None:
        self.process_file(infile, outfile, imagetype=self.imagetype,
                          denoise=self.denoise, workflow=self.workflow,
                          waifu_executable=self.waifu_executable,
                          automator_executable=self.automator_executable,
                          verbosity=self.pipeline.verbosity)

    # region Public Class Methods

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
            "-w", "--waifu_executable",
            default="waifu",
            dest="waifu_executable",
            type=str,
            help="path to waifu executable")
        parser.add_argument(
            "-t", "--type",
            default="a",
            dest="imagetype",
            type=str,
            help="image type - a for anime (default), p for photo")
        parser.add_argument(
            "-n", "--noise",
            default=1,
            dest="denoise",
            type=int,
            help="denoise level (0-4)")
        parser.add_argument(
            "-a", "--automator_executable",
            default="automator",
            dest="automator_executable",
            type=str,
            help="path to automator executable")
        parser.add_argument(
            "-r", "--workflow",
            dest="workflow",
            required=True,
            type=str,
            help="path to workflow")

        return parser

    @classmethod
    def process_file(cls, infile: str, outfile: str, waifu_executable: str,
                     imagetype: str, denoise: str, automator_executable: str,
                     workflow: str, verbosity: int):

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
        command = f"{waifu_executable} " \
                  f"-t {imagetype} " \
                  f"-s 2 " \
                  f"-n {denoise} " \
                  f"-i {waifu_infile} " \
                  f"-o {waifu_outfile.name}"
        if verbosity >= 1:
            print(cls.get_indented_text(command))
        Popen(command, shell=True, close_fds=True).wait()
        if tempfile is not None:
            Image.open(waifu_outfile.name).crop(
                (0, 0, original_size[0] * 2,
                 original_size[1] * 2)).save(waifu_outfile.name)
            remove(tempfile.name)
        waifu_2x_image = Image.open(waifu_outfile.name)
        remove(waifu_outfile.name)

        # Pixelmator 3X
        pixelmator_tempfile = NamedTemporaryFile(delete=False, suffix=".png")
        copyfile(infile, pixelmator_tempfile.name)
        command = f"{automator_executable} " \
                  f"-i {pixelmator_tempfile.name} " \
                  f"{workflow}"
        if verbosity >= 1:
            print(cls.get_indented_text(command))
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

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    WaifuPixelmator2xTransparentProcessor.main()
