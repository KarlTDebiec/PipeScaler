#!/usr/bin/env python
#   pipescaler/processors/waifu_processor.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
""""""
from __future__ import annotations

from argparse import ArgumentParser
I'lfrom inspect import cleandoc, getfile
from logging import info
from os.path import dirname, join
from typing import Any

import chainer
import numpy as np
from PIL import Image
from waifu2x.reconstruct import blockwise
from waifu2x.srcnn import archs

from pipescaler.common import (
    validate_int,
    validate_str,
)
from pipescaler.core import (
    Processor,
    UnsupportedImageModeError,
    crop_image,
    expand_image,
    remove_palette_from_image,
)

model_architectures = {k.lower(): v for k, v in archs.items()}


class WaifuProcessor(Processor):
    """Upscales and/or denoises using [waifu2x](https://github.com/nagadomi/waifu2x)."""

    architectures = {"resnet10", "upconv7", "upresnet10", "vgg7"}

    def __init__(
        self,
        architecture: str = "upconv7",
        denoise: int = 1,
        scale: int = 2,
        device: str = "cuda",
        **kwargs: Any,
    ) -> None:
        """
        Validates and stores static configuration.

        Arguments:
            architecture (str): Model architecture
            denoise (int): Level of denoising to apply
            scale (int): Output image scale
            device (str): Device on which to compute
        """
        super().__init__(**kwargs)

        # Store configuration
        self.architecture = validate_str(architecture, self.architectures)
        self.scale = validate_int(scale, min_value=1, max_value=2)
        self.denoise = validate_int(denoise, min_value=0, max_value=4)
        if device == "cuda":
            chainer.backends.cuda.get_device_from_id(0).use()

        # Load model(s)
        model_directory = join(
            dirname(getfile(blockwise)), "models", self.architecture.lower()
        )
        if self.architecture in ("resnet10", "vgg7"):
            model_1_infile = join(
                model_directory, f"anime_style_noise{self.denoise}_rgb.npz"
            )
            self.model_1 = model_architectures[self.architecture](3)
            chainer.serializers.load_npz(model_1_infile, self.model_1)
            if self.scale == 2:
                model_2_infile = join(model_directory, f"anime_style_scale_rgb.npz")
                self.model_2 = model_architectures[self.architecture](3)
                chainer.serializers.load_npz(model_2_infile, self.model_2)
            else:
                self.model_2 = None
        else:
            model_1_infile = join(
                model_directory, f"anime_style_noise{self.denoise}_scale_rgb.npz"
            )
            self.model_1 = model_architectures[self.architecture](3)
            chainer.serializers.load_npz(model_1_infile, self.model_1)
            self.model_2 = None

    def process_file(self, infile: str, outfile: str) -> None:
        """
        Loads image, processes it, and saves resulting output.

        Arguments:
            infile (str): Input file
            outfile (str): Output file
        """
        # Read image
        input_image = Image.open(infile)
        if input_image.mode == "P":
            input_image = remove_palette_from_image(input_image)
        if input_image.mode == "RGB":
            expanded_image = expand_image(input_image, 8, 8, 8, 8)
        elif input_image.mode == "L":
            expanded_image = expand_image(input_image.convert("RGB"), 8, 8, 8, 8)
        else:
            raise UnsupportedImageModeError(
                f"Image mode '{input_image.mode}' of image '{infile}'"
                f" is not supported by {type(self)}"
            )
        expanded_datum = np.array(expanded_image)

        # Process image
        waifued_datum = blockwise(expanded_datum, self.model_1, 128, 16)
        waifued_datum = np.clip(waifued_datum, 0, 1) * 255
        if self.model_2 is not None:
            waifued_datum = blockwise(waifued_datum, self.model_2, 128, 16)
            waifued_datum = np.clip(waifued_datum, 0, 1) * 255
        waifued_image = Image.fromarray(waifued_datum.astype(np.uint8))
        crop_scale = waifued_datum.shape[0] / expanded_datum.shape[0]
        cropped_image = crop_image(
            waifued_image,
            8 * crop_scale,
            8 * crop_scale,
            8 * crop_scale,
            8 * crop_scale,
        )
        if cropped_image.size != (
            input_image.size[0] * self.scale,
            input_image.size[1] * self.scale,
        ):
            cropped_image = cropped_image.resize(
                (input_image.size[0] * self.scale, input_image.size[1] * self.scale),
                resample=Image.LANCZOS,
            )
        if input_image.mode == "L":
            cropped_image = cropped_image.convert("L")

        # Write image
        cropped_image.save(outfile)
        info(f"{self}: '{outfile}' saved")

    @classmethod
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """
        Constructs argument parser.

        Returns:
            parser (ArgumentParser): Argument parser
        """
        description = kwargs.get("description", cleandoc(cls.__doc__))
        parser = super().construct_argparser(description=description, **kwargs)

        # Operations
        parser.add_argument(
            "--architecture",
            default="upconv7",
            type=cls.str_arg(cls.architectures),
            help=f"model architecture, (options: {cls.architectures}, default: "
            "%(default)s)",
        )
        parser.add_argument(
            "--denoise",
            default=1,
            type=cls.int_arg(min_value=0, max_value=3),
            help="denoise level (0-4, default: %(default)s)",
        )
        parser.add_argument(
            "--scale",
            default=2,
            type=cls.int_arg(min_value=1, max_value=2),
            help="scale factor (1 or 2, default: %(default)s)",
        )
        parser.add_argument(
            "--device",
            default="cuda",
            type=cls.str_arg(options=["cpu", "cuda"]),
            help="device (default: %(default)s)",
        )

        return parser


if __name__ == "__main__":
    WaifuProcessor.main()
