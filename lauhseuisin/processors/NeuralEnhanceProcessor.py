#!python
#   lauhseuisin/processors/NeuralEnhanceProcessor.py
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
class NeuralEnhanceProcessor(Processor):

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.desc = "pm2x"

    @classmethod
    def process_file(cls, infile: str, outfile: str, verbosity: int):

        input_image = Image.open(infile)

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
        rgba_image = Image.open(tempfile.name)
        remove(tempfile.name)


#################################### MAIN #####################################
if __name__ == "__main__":
    NeuralEnhanceProcessor.main()
