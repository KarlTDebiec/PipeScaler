#!/usr/bin/env python
#   pipescaler/processors/external/waifu_external_processor.py
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
from logging import debug
from platform import system
from typing import Any

from PIL import Image

from pipescaler.common import (
    run_command,
    temporary_filename,
    validate_executable,
    validate_int,
    validate_str,
)
from pipescaler.core import (
    ExternalProcessor,
    crop_image,
    expand_image,
    validate_image_and_convert_mode,
)


class WaifuExternalProcessor(ExternalProcessor):
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
            expand: Whether to expand and crop image
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

    @property
    def command_template(self):
        """String template with which to generate command"""
        command = (
            f"{validate_executable(self.executable, self.supported_platforms)}"
            f" -s {self.scale}"
            f" -n {self.denoise}"
        )
        if system() == "Windows":
            command += " -p gpu"
        command += ' -i "{infile}" -o "{outfile}"'

        return command

    @property
    def executable(self) -> str:
        """Name of executable"""
        if system() == "Windows":
            return "waifu2x-caffe-cui.exe"
        return "waifu2x"

    def process(self, infile: str, outfile: str) -> None:
        """
        Read image from infile, process it, and save to outfile

        Arguments:
            infile: Input file path
            outfile: Output file path
        """
        input_image, input_mode = validate_image_and_convert_mode(
            infile, ["1", "L", "RGB"], "RGB"
        )

        with temporary_filename(".png") as intermediate_file_1:
            if self.expand:
                intermediate_image = expand_image(input_image, 8, 8, 8, 8, 200)
            else:
                intermediate_image = input_image.copy()
            intermediate_image.save(intermediate_file_1)

            with temporary_filename(".png") as intermediate_file_2:
                command = self.command_template.format(
                    infile=intermediate_file_1, outfile=intermediate_file_2
                )
                debug(f"{self}: {command}")
                run_command(command)

                output_image = Image.open(intermediate_file_2)
                if self.expand:
                    output_image = crop_image(
                        output_image,
                        (output_image.width - (input_image.width * self.scale)) // 2,
                        (output_image.height - (input_image.height * self.scale)) // 2,
                        (output_image.width - (input_image.width * self.scale)) // 2,
                        (output_image.height - (input_image.height * self.scale)) // 2,
                    )
                if output_image.mode != input_mode:
                    output_image = output_image.convert(input_mode)

        output_image.save(outfile)

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
