#!/usr/bin/env python
#   pipescaler/processors/waifupixelmator2x_processor.py
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
from shutil import copyfile
from subprocess import Popen
from tempfile import NamedTemporaryFile
from typing import Any

import numpy as np
from PIL import Image

from pipescaler.common import package_root
from pipescaler.processors.processor import Processor


################################### CLASSES ###################################
class WaifuPixelmator2xProcessor(Processor):

    # region Builtins

    def __init__(self, imagetype: str = "a", denoise: str = 1, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.imagetype = imagetype
        self.scale = 2
        self.denoise = denoise

        # endregion

    # region Properties

    @property
    def desc(self) -> str:
        """str: Description"""
        if not hasattr(self, "_desc"):
            return f"waifupm2xalpha-" f"{self.imagetype}-{self.scale}-{self.denoise}"
        return self._desc

    # endregion

    # region Methods

    def process_file_in_pipeline(self, infile: str, outfile: str) -> None:
        self.process_file(
            infile,
            outfile,
            imagetype=self.imagetype,
            denoise=self.denoise,
            verbosity=self.pipeline.verbosity,
        )

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
            help="image type - a for anime, p for photo, (default: " "%(default)s)",
        )
        parser.add_argument(
            "--denoise",
            default=1,
            dest="denoise",
            type=int,
            help="denoise level (0-4, default: %(default)s)",
        )

        return parser

    @classmethod
    def process_file(
        cls, infile: str, outfile: str, verbosity: int = 1, **kwargs: Any
    ) -> None:
        imagetype = kwargs.get("imagetype")
        denoise = kwargs.get("denoise")

        workflow = f"{package_root}/data/workflows/3x.workflow"
        if not isdir(workflow):
            raise ValueError()

        # Prepare temporary image with reflections and minimum size of 200x200
        image = Image.open(infile)
        w, h = image.size
        transposed_h = image.transpose(Image.FLIP_LEFT_RIGHT)
        transposed_v = image.transpose(Image.FLIP_TOP_BOTTOM)
        transposed_hv = transposed_h.transpose(Image.FLIP_TOP_BOTTOM)
        reflected = Image.new(
            image.mode, (max(200, int(w * 1.5)), max(200, int(h * 1.5)))
        )
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
        reflected = reflected.convert("RGB")
        tempfile_1 = NamedTemporaryFile(delete=False, suffix=".png")
        reflected.save(tempfile_1)
        tempfile_1.close()

        # Upscale using waifu
        tempfile_2 = NamedTemporaryFile(delete=False, suffix=".png")
        tempfile_2.close()
        command = (
            f"waifu2x "
            f"-t {imagetype} "
            f"-s 2 "
            f"-n {denoise} "
            f"-i {tempfile_1.name} "
            f"-o {tempfile_2.name}"
        )
        if verbosity >= 1:
            print(command)
        Popen(command, shell=True, close_fds=True).wait()

        # Load processed image and crop back to original content
        waifu_2x_image = Image.open(tempfile_2.name).crop(
            ((x - w // 2) * 2, (y - h // 2) * 2, (x + w // 2) * 2, (y + h // 2) * 2)
        )
        remove(tempfile_1.name)
        remove(tempfile_2.name)

        # Pixelmator 3X
        tempfile_3 = NamedTemporaryFile(delete=False, suffix=".png")
        tempfile_3.close()
        copyfile(infile, tempfile_3.name)
        command = f"automator " f"-i {tempfile_3.name} " f"{workflow}"
        if verbosity >= 1:
            print(command)
        Popen(command, shell=True, close_fds=True).wait()
        pixelmator_3x_image = Image.open(tempfile_3.name)
        remove(tempfile_3.name)

        # Scale Pixelmator down to 2X
        pixelmator_2x_image = pixelmator_3x_image.resize(
            (
                int(np.round(pixelmator_3x_image.size[0] * 0.66667)),
                int(np.round(pixelmator_3x_image.size[1] * 0.66667)),
            ),
            resample=Image.LANCZOS,
        )

        # Paste pixelmator, then waifu, then set alpha to pixelmator's
        merged_image = Image.new("RGB", pixelmator_2x_image.size)
        merged_image.paste(pixelmator_2x_image.convert("RGB"))
        merged_image.paste(waifu_2x_image)
        merged_data = np.zeros(
            (merged_image.size[1], merged_image.size[0], 4), np.uint8
        )
        merged_data[:, :, :3] = np.array(merged_image)
        merged_data[:, :, 3] = np.array(pixelmator_2x_image)[:, :, 3]
        final_image = Image.fromarray(merged_data)

        # Save final image
        final_image.save(outfile)

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    WaifuPixelmator2xProcessor.main()
