#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for image processors that use PyTorch."""
from __future__ import annotations

from abc import ABC
from typing import Any

import numpy as np
import torch
from PIL import Image

from pipescaler.common import validate_input_file
from pipescaler.image.core.operators.image_processor import ImageProcessor
from pipescaler.image.core.validation import validate_image_and_convert_mode


class PyTorchImageProcessor(ImageProcessor, ABC):
    """Abstract base class for image processors that use PyTorch."""

    def __init__(self, model_infile: str, **kwargs: Any) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            model_infile: Path to model file
            kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        self.model_infile = validate_input_file(model_infile)
        self.model = torch.load(self.model_infile)
        """Neural network model."""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        """Name of device on which to run neural network model."""

    def __call__(self, input_image: Image.Image) -> Image.Image:
        """Process an image.

        Arguments:
            input_image: Input image
        Returns:
            Processed output image
        """
        input_image, output_mode = validate_image_and_convert_mode(
            input_image, self.inputs()["input"], "RGB"
        )

        input_array = np.array(input_image)

        output_array = self.upscale(input_array)
        output_image = Image.fromarray(output_array)
        if output_image.mode != output_mode:
            output_image = output_image.convert(output_mode)

        return output_image

    def __repr__(self) -> str:
        """Representation."""
        return f"{self.__class__.__name__}(model_infile={self.model_infile!r})"

    def upscale(self, input_array: np.ndarray) -> np.ndarray:
        """Upscale an image array.

        Arguments:
            input_array: Array to upscale
        Returns:
            Upscaled array
        """
        input_array = input_array * 1.0 / 255
        input_array = np.transpose(input_array[:, :, [2, 1, 0]], (2, 0, 1))
        input_tensor = torch.from_numpy(input_array)
        input_tensor = input_tensor.float().unsqueeze(0).to(self.device)

        output_tensor = self.model(input_tensor).data.squeeze().float().cpu()
        output_array: np.ndarray = output_tensor.clamp_(0, 1).numpy()
        output_array = np.transpose(output_array[[2, 1, 0], :, :], (1, 2, 0))
        output_array = np.array(output_array * 255, np.uint8)

        return output_array

    @classmethod
    def inputs(cls) -> dict[str, tuple[str, ...]]:
        """Inputs to this operator."""
        return {
            "input": ("1", "L", "RGB"),
        }

    @classmethod
    def outputs(cls) -> dict[str, tuple[str, ...]]:
        """Outputs of this operator."""
        return {
            "output": ("1", "L", "RGB"),
        }
