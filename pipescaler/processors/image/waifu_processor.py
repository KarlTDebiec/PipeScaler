#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Upscales and/or denoises image using Waifu2x via PyTorch."""
from __future__ import annotations

from logging import warning
from typing import Any

import numpy as np
import torch
from PIL import Image

from pipescaler.common import validate_input_path
from pipescaler.core import ImageProcessor, convert_mode


class WaifuProcessor(ImageProcessor):
    """Upscales and/or denoises image using Waifu2x via PyTorch.

    See [waifu2x](https://github.com/nagadomi/waifu2x).
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
            warning(
                f"{self}: Torch raised '{error}' with device '{device}', "
                f"falling back to cpu"
            )

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
    @property
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links."""
        return (
            "Upscales and/or denoises image using [Waifu2x]"
            "(https://github.com/nagadomi/waifu2x) via PyTorch."
        )

    @classmethod
    @property
    def supported_input_modes(self) -> list[str]:
        """Supported modes for input image"""
        return ["L", "RGB"]
