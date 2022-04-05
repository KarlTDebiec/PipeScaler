#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Base class for processors that perform their processing within python."""
from __future__ import annotations

from abc import ABC
from typing import Any

import numpy as np
import torch
from PIL import Image
from torch.nn import Module

from pipescaler.common import validate_input_path
from pipescaler.core import convert_mode
from pipescaler.core.image_processor import ImageProcessor


class PyTorchProcessor(ImageProcessor, ABC):
    """Base class for processors that perform their processing using PyTorch."""

    def __init__(self, model_infile: str, **kwargs: Any) -> None:
        """Validate configuration and initialize.

        Arguments:
            model_infile: Path to model infile
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        self.model_infile = validate_input_path(model_infile)

    def process(self, input_image: Image.Image) -> Image.Image:
        """Process an image.

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
        if output_image.mode != input_mode:
            output_image = output_image.convert(input_mode)

        return output_image

    def upscale(self, input_array):
        """Upscale an image array.

        Arguments:
            input_array: Array to upscale
        Returns:
            Upscaled array
        """
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

    @property
    def device(self) -> str:
        """Name of device on which to run neural network model."""
        return self._device

    @device.setter
    def device(self, value: str) -> None:
        self._device = value

    @property
    def model(self) -> Module:
        """Neural network model."""
        return self._model

    @model.setter
    def model(self, value: Module):
        self._model = value

    @classmethod
    @property
    def supported_input_modes(self) -> list[str]:
        """Supported modes for input image."""
        return ["1", "L", "RGB"]
