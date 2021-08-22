#!/usr/bin/env python
#   pipescaler/processors/waifu_processor.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""
Processes an image using waifu.
Requires the macOS version of waifu2x (https://github.com/imxieyi/waifu2x-mac)
in the executor's path.
Provides two improvements over running waifu2x directly:
1. If image is below waifu2x's minimum size, expands canvas.
2. Eliminates edge effects by reflecting image around edges.
"""
####################################### MODULES ########################################
from __future__ import annotations

from argparse import ArgumentParser
from logging import debug, info
from os import remove
from platform import win32_ver
from subprocess import PIPE, Popen
from tempfile import NamedTemporaryFile
from typing import Any

from PIL import Image

from pipescaler.common import (
    validate_executable,
    validate_int,
    validate_str,
)
from pipescaler.core import (
    Processor,
    UnsupportedImageModeError,
    remove_palette_from_image,
)


####################################### CLASSES ########################################
class WaifuExternalProcessor(Processor):
    models = {"windows": ["a"], "unix": ["a", "p"]}

    # region Builtins

    def __init__(
        self,
        imagetype: str = "a",
        denoise: int = 1,
        scale: int = 2,
        expand: bool = True,
        **kwargs: Any,
    ) -> None:
        """
        Validates and stores static configuration.

        Arguments:
            imagetype (str): Image type
            denoise (int): Level of denoising to apply
            scale (int): Output image scale
            expand (str): Whether or not to expand and crop image
        """
        super().__init__(**kwargs)

        # Store configuration
        self.imagetype = validate_str(
            imagetype,
            self.models["windows"] if any(win32_ver()) else self.models["unix"],
        )
        self.scale = validate_int(scale, min_value=1, max_value=2)
        self.denoise = validate_int(denoise, min_value=0, max_value=4)
        self.expand = expand

    def __call__(self, infile: str, outfile: str) -> None:
        """
        Processes infile and writes the resulting output to outfile.

        Arguments:
            infile (str): Input file
            outfile (str): Output file
        """
        if any(win32_ver()):
            validate_executable("waifu2x-caffe-cui.exe")
        else:
            validate_executable("waifu2x")
        super().__call__(infile, outfile)

    # endregion

    # region Methods

    def process_file(self, infile: str, outfile: str) -> None:
        """
        Loads image, processes it, and saves resulting output

        Arguments:
            infile (str): Input file
            outfile (str): Output file
        """
        if any(win32_ver()):
            executable = validate_executable("waifu2x-caffe-cui.exe")
        else:
            executable = validate_executable("waifu2x")

        # Read image
        input_image = Image.open(infile)
        if input_image.mode == "P":
            input_image = remove_palette_from_image(input_image)
        if input_image.mode == "RGB":
            temp_image = input_image
        elif input_image.mode == "L":
            temp_image = input_image.convert("RGB")
        else:
            raise UnsupportedImageModeError(
                f"Image mode '{input_image.mode}' of image '{infile}'"
                f" is not supported by {type(self)}"
            )

        tempfile = NamedTemporaryFile(delete=False, suffix=".png")
        if self.expand:
            w, h = temp_image.size
            transposed_h = temp_image.transpose(Image.FLIP_LEFT_RIGHT)
            transposed_v = temp_image.transpose(Image.FLIP_TOP_BOTTOM)
            transposed_hv = temp_image.transpose(Image.FLIP_TOP_BOTTOM)
            reflected = Image.new(
                temp_image.mode, (max(200, int(w * 1.5)), max(200, int(h * 1.5)))
            )
            x = reflected.size[0] // 2
            y = reflected.size[1] // 2
            reflected.paste(temp_image, (x - w // 2, y - h // 2))
            reflected.paste(transposed_h, (x + w // 2, y - h // 2))
            reflected.paste(transposed_h, (x - w - w // 2, y - h // 2))
            reflected.paste(transposed_v, (x - w // 2, y - h - h // 2))
            reflected.paste(transposed_v, (x - w // 2, y + h // 2))
            reflected.paste(transposed_hv, (x + w // 2, y - h - h // 2))
            reflected.paste(transposed_hv, (x - w - w // 2, y - h - h // 2))
            reflected.paste(transposed_hv, (x - w - w // 2, y + h // 2))
            reflected.paste(transposed_hv, (x + w // 2, y + h // 2))
            reflected.save(tempfile)
        else:
            temp_image.save(tempfile)
        tempfile.close()

        # Process using waifu
        command = f"{executable} -p gpu"
        if not any(win32_ver()):
            command += f" -t {self.imagetype}"
        command += f" -s {self.scale}"
        command += f" -n {self.denoise}"
        command += f' -i "{tempfile.name}"'
        command += f' -o "{outfile}"'
        debug(command)
        child = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        exitcode = child.wait(600)
        if exitcode != 0:
            raise ValueError()  # TODO: Provide useful output

        # Load processed image and crop back to original content
        waifued_image = Image.open(outfile)
        remove(tempfile.name)
        if self.expand:
            waifued_image = waifued_image.crop(
                (
                    (x - w // 2) * self.scale,
                    (y - h // 2) * self.scale,
                    (x + w // 2) * self.scale,
                    (y + h // 2) * self.scale,
                )
            )
        if input_image.mode == "L":
            waifued_image = waifued_image.convert("L")

        # Write image
        waifued_image.save(outfile)
        info(f"{self}: '{outfile}' saved")

    # endregion

    # region Class Methods

    @classmethod
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """
        Constructs argument parser.
        Returns:
            parser (ArgumentParser): Argument parser
        """
        description = kwargs.get("description", __doc__.strip())
        parser = super().construct_argparser(description=description, **kwargs)

        # Operations
        parser.add_argument(
            "--type",
            default="a",
            dest="imagetype",
            type=cls.str_arg(
                cls.models["windows"] if any(win32_ver()) else cls.models["unix"],
            ),
            help="image type - a for anime, p for photo, (default: " "%(default)s)",
        )
        parser.add_argument(
            "--denoise",
            default=1,
            dest="denoise",
            type=cls.int_arg(min_value=0, max_value=4),
            help="denoise level (0-4, default: %(default)s)",
        )
        parser.add_argument(
            "--scale",
            default=2,
            dest="scale",
            type=cls.int_arg(min_value=1, max_value=2),
            help="scale factor (1 or 2, default: %(default)s)",
        )

        return parser

    # endregion


######################################### MAIN #########################################
if __name__ == "__main__":
    WaifuExternalProcessor.main()
