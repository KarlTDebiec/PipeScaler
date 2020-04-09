#!python
#   lauhseuisin/processors/Pixelmator2xProcessor.py
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

from lauhseuisin import package_root
from lauhseuisin.processors.Processor import Processor


################################### CLASSES ###################################
class Pixelmator2xProcessor(Processor):

    def __init__(self, keep_transparent: bool = False, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.split_alpha = keep_transparent
        if not self.split_alpha:
            self.desc = "pm2x"
        else:
            self.desc = "pm2x-rgb+a"

    def process_file_in_pipeline(self, infile: str, outfile: str) -> None:
        self.process_file(infile, outfile, self.split_alpha,
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
            "--keep_transparent",
            default=False,
            dest="keep_transparent",
            type=bool,
            help="scale using RGB and RGBA, then combine RGB with alpha from "
                 "RGBA; useful if transparent region of image contains "
                 "data that needs to be retained")

        return parser

    @classmethod
    def process_file(cls, infile: str, outfile: str, keep_transparent: bool,
                     verbosity: int):

        workflow = f"{package_root}/data/workflows/3x.workflow"
        if not isdir(workflow):
            raise ValueError()
        input_image = Image.open(infile)

        # Pixelmator 3X RGB
        if keep_transparent:
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

        # Pixelmator 3X RGBA
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

        # Combine R, G, and B from RGB with A from RGBA
        if keep_transparent:
            merged_data = np.zeros((rgb_image.size[1], rgb_image.size[0], 4),
                                   np.uint8)
            merged_data[:, :, :3] = np.array(rgb_image)
            merged_data[:, :, 3] = np.array(rgba_image)[:, :, 3]
            rgba_image = Image.fromarray(merged_data)

        # Save image
        rgba_image.save(outfile)


#################################### MAIN #####################################
if __name__ == "__main__":
    Pixelmator2xProcessor.main()
