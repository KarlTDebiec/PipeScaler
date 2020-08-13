#!/usr/bin/env python
#   pipescaler/processors/Pixelmator2xProcessor.py
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
from os.path import isdir
from subprocess import Popen
from tempfile import NamedTemporaryFile
from typing import Any

import numpy as np
from PIL import Image

from pipescaler.common import package_root
from pipescaler.processors.Processor import Processor


################################### CLASSES ###################################
class Pixelmator2xProcessor(Processor):

    def __init__(self, sepalpha: bool = False, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.sepalpha = sepalpha
        if not self.sepalpha:
            self.desc = "pm2x"
        else:
            self.desc = "pm2x-rgb+a"

    def process_file_in_pipeline(self, infile: str, outfile: str) -> None:
        self.process_file(infile, outfile, self.sepalpha,
                          self.pipeline.verbosity)

    @classmethod
    def construct_argparser(cls) -> ArgumentParser:
        """
        Constructs argument parser

        Returns:
            parser (ArgumentParser): Argument parser
        """
        parser = super().construct_argparser(description=__doc__)

        parser.add_argument(
            "--sepalpha",
            action="store_true",
            dest="sepalpha",
            help="if an alpha channel is present, scale separately using RGB "
                 "and RGBA, then combine RGB with alpha from RGBA; useful if "
                 "alpha channel data does not represent transparency")

        return parser

    @classmethod
    def process_file(cls, infile: str, outfile: str, sepalpha: bool,
                     verbosity: int):

        workflow = f"{package_root}/data/workflows/3x.workflow"
        if not isdir(workflow):
            raise ValueError()
        input_image = Image.open(infile)

        # RGB or RGBA with transparency handled simultaneously
        if input_image.mode == "RGB" or not sepalpha:
            tempfile = NamedTemporaryFile(delete=False, suffix=".png")
            tempfile.close()
            input_image.save(tempfile.name)
            command = f"automator " \
                      f"-i {tempfile.name} " \
                      f"{workflow}"
            if verbosity >= 1:
                print(command)
            Popen(command, shell=True, close_fds=True).wait()
            output_image = Image.open(tempfile.name).resize(
                (int(np.round(input_image.size[0] * 2)),
                 int(np.round(input_image.size[1] * 2))),
                resample=Image.LANCZOS)
            remove(tempfile.name)

        # RGBA with sepalph
        else:
            # 2X with only RGB channels
            tempfile = NamedTemporaryFile(delete=False, suffix=".png")
            tempfile.close()
            input_image.convert("RGB").save(tempfile.name)
            command = f"automator " \
                      f"-i {tempfile.name} " \
                      f"{workflow}"
            if verbosity >= 1:
                print(command)
            Popen(command, shell=True, close_fds=True).wait()
            rgb_image = Image.open(tempfile.name).resize(
                (int(np.round(input_image.size[0] * 2)),
                 int(np.round(input_image.size[1] * 2))),
                resample=Image.LANCZOS)
            remove(tempfile.name)

            # 2X with all channels
            tempfile = NamedTemporaryFile(delete=False, suffix=".png")
            tempfile.close()
            input_image.save(tempfile.name)
            command = f"automator " \
                      f"-i {tempfile.name} " \
                      f"{workflow}"
            if verbosity >= 1:
                print(command)
            Popen(command, shell=True, close_fds=True).wait()
            rgba_image = Image.open(tempfile.name).resize(
                (int(np.round(input_image.size[0] * 2)),
                 int(np.round(input_image.size[1] * 2))),
                resample=Image.LANCZOS)
            remove(tempfile.name)

            # Merge RGB from former with A from latter
            merged_data = np.zeros((rgb_image.size[1], rgb_image.size[0], 4),
                                   np.uint8)
            merged_data[:, :, :3] = np.array(rgb_image)
            merged_data[:, :, 3] = np.array(rgba_image)[:, :, 3]
            output_image = Image.fromarray(merged_data)

        # Save image
        output_image.save(outfile)


#################################### MAIN #####################################
if __name__ == "__main__":
    Pixelmator2xProcessor.main()
