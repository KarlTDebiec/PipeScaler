#!/usr/bin/env python
#   pipescaler/processors/image/waifu_processor.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Upscales and/or denoises image using Waifu2x"""
from __future__ import annotations

from argparse import ArgumentParser
from inspect import cleandoc
from logging import warning
from typing import Any, List

import numpy as np
import torch
from PIL import Image

from pipescaler.common import validate_input_path
from pipescaler.core import ImageProcessor, convert_mode


class WaifuProcessor(ImageProcessor):
    """
    Upscales and/or denoises image using [waifu2x](https://github.com/nagadomi/waifu2x)
    """

    def __init__(self, model_infile: str, device: str = "cuda", **kwargs: Any) -> None:
        """
        Validate and store static configuration

        Arguments:
            model_infile: Path to model infile
            device: Device on which to compute
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        self.model_infile = validate_input_path(model_infile)
        model = torch.load(model_infile)
        model.eval()
        try:
            self.model = model.to(device)
            self.device = device
        except AssertionError as error:
            device = "cpu"
            self.model = model.to(device)
            self.device = device
            warning(f"{self}: Torch raised '{error}' with device '{device}', "
                    f"falling back to cpu")

    @property
    def supported_input_modes(self) -> List[str]:
        """Supported modes for input image"""
        return ["L", "RGB"]

    def process(self, input_image: Image.Image) -> Image.Image:
        """
        Process an image

        Arguments:
            input_image: Input image to process
        Returns:
            Processed output image
        """
        input_image, input_mode = convert_mode(input_image, "RGB")
        # noinspection PyTypeChecker
        input_array = np.array(input_image)

        output_array = self.upscale(input_array)
        output_image = Image.fromarray(output_array)
        if input_mode == "L":
            output_image = output_image.convert("L")

        return output_image

    def upscale(self, input_array):
        input_array = input_array * 1.0 / 255
        input_array = np.transpose(input_array[:, :, [2, 1, 0]], (2, 0, 1))
        input_array = torch.from_numpy(input_array).float()
        input_array = input_array.unsqueeze(0).to(self.device)

        output_array = (
            self.model(input_array).data.squeeze().float().cpu().clamp_(0, 1).numpy()
        )
        output_array = np.transpose(output_array[[2, 1, 0], :, :], (1, 2, 0))
        output_array = np.array(output_array * 255, np.uint8)

        return output_array

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

        # Input
        parser.add_argument(
            "--model",
            dest="model_infile",
            required=True,
            type=cls.input_path_arg(),
            help="model input file",
        )

        # Operations
        parser.add_argument(
            "--device",
            default="cuda",
            type=cls.str_arg(options=["cpu", "cuda"]),
            help="device (default: %(default)s)",
        )

        return parser


if __name__ == "__main__":
    WaifuProcessor.main()
