#!/usr/bin/env python
#   pipescaler/processors/waifu_external_processor.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Upscales and/or denoises image using waifu2x"""
from __future__ import annotations

from argparse import ArgumentParser
from inspect import cleandoc
from logging import debug, info
from os import remove
from platform import system
from tempfile import NamedTemporaryFile
from typing import Any

from PIL import Image

from pipescaler.common import (
    run_command,
    validate_executable,
    validate_int,
    validate_str,
)
from pipescaler.core import Processor, validate_image_and_convert_mode


class WaifuExternalProcessor(Processor):
    """
    Upscales and/or denoises image using [waifu2x](https://github.com/nagadomi/waifu2x)

    On Windows, requires [waifu2x-caffe](https://github.com/lltcggie/waifu2x-caffe) in
    the executor's path.

    On Linux, support is untested but likely achievable with minimal effort.

    On macOS, requires [waifu2x-mac](https://github.com/imxieyi/waifu2x-mac) in the
    executor's path.

    Provides two improvements over running waifu2x directly:
    1. If image is below waifu2x's minimum size, expands canvas.
    2. Eliminates edge effects by reflecting image around edges.
    """

    models = {"windows": ["a"], "unix": ["a", "p"]}

    def __init__(
        self,
        imagetype: str = "a",
        denoise: int = 1,
        scale: int = 2,
        expand: bool = True,
        **kwargs: Any,
    ) -> None:
        """
        Validate and store static configuration

        Arguments:
            imagetype: Image type
            denoise: Level of denoising to apply
            scale: Output image scale
            expand: Whether or not to expand and crop image
        """
        super().__init__(**kwargs)

        # Store configuration
        self.imagetype = validate_str(
            imagetype,
            self.models["windows"] if system() == "Windows" else self.models["unix"],
        )
        self.scale = validate_int(scale, min_value=1, max_value=2)
        self.denoise = validate_int(denoise, min_value=0, max_value=4)
        self.expand = expand

    def __call__(self, infile: str, outfile: str) -> None:
        """
        Read image from infile, process it, and save to outfile

        Arguments:
            infile: Input file path
            outfile: Output file path
        """
        if system() == "Windows":
            command = (
                validate_executable("waifu2x-caffe-cui.exe", {"Windows"}) + " -p gpu"
            )
        else:
            command = (
                validate_executable("waifu2x", {"Darwin", "Linux"})
                + f" -t {self.imagetype}"
            )

        # Read image
        input_image, input_mode = validate_image_and_convert_mode(
            infile, ["1", "L", "RGB"], "RGB"
        )

        tempfile = NamedTemporaryFile(delete=False, suffix=".png")
        if self.expand:
            w, h = input_image.size
            transposed_h = input_image.transpose(Image.FLIP_LEFT_RIGHT)
            transposed_v = input_image.transpose(Image.FLIP_TOP_BOTTOM)
            transposed_hv = input_image.transpose(Image.FLIP_TOP_BOTTOM)
            reflected = Image.new(
                "RGB", (max(200, int(w * 1.5)), max(200, int(h * 1.5)))
            )
            x = reflected.size[0] // 2
            y = reflected.size[1] // 2
            reflected.paste(input_image, (x - w // 2, y - h // 2))
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
            input_image.save(tempfile)
        tempfile.close()

        # Process using waifu
        command += (
            f" -s {self.scale}"
            f" -n {self.denoise}"
            f' -i "{tempfile.name}"'
            f' -o "{outfile}"'
        )
        debug(f"{self}: {command}")
        run_command(command)

        # Load processed image and crop back to original content
        output_image = Image.open(outfile)
        remove(tempfile.name)
        if self.expand:
            output_image = output_image.crop(
                (
                    (x - w // 2) * self.scale,
                    (y - h // 2) * self.scale,
                    (x + w // 2) * self.scale,
                    (y + h // 2) * self.scale,
                )
            )
        if output_image.mode != input_mode:
            output_image = output_image.convert(input_mode)

        # Write image
        output_image.save(outfile)
        info(f"{self}: '{outfile}' saved")

    @classmethod
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """
        Construct argument parser

        Arguments:
            **kwargs: Additional keyword arguments

        Returns:
            parser: Argument parser
        """
        description = kwargs.pop(
            "description", cleandoc(cls.__doc__) if cls.__doc__ is not None else ""
        )
        parser = super().construct_argparser(description=description, **kwargs)

        # Operations
        parser.add_argument(
            "--type",
            default="a",
            dest="imagetype",
            type=cls.str_arg(
                cls.models["windows"] if system() == "Windows" else cls.models["unix"],
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


if __name__ == "__main__":
    WaifuExternalProcessor.main()
