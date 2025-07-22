#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for image processors that use PyTorch."""

from __future__ import annotations

from abc import ABC
from pathlib import Path
from typing import Any

import numpy as np
import torch
from PIL import Image

from pipescaler.common.validation import val_input_path
from pipescaler.image.core.operators import ImageProcessor
from pipescaler.image.core.typing import ImageMode
from pipescaler.image.core.validation import validate_image_and_convert_mode


class PyTorchImageProcessor(ImageProcessor, ABC):
    """Abstract base class for image processors that use PyTorch."""

    def __init__(self, model_input_path: Path | str, **kwargs: Any) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            model_input_path: Path to model file
            kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        self.model_input_path = val_input_path(model_input_path)
        self.model = torch.load(self.model_input_path)
        """Neural network model."""
        self.device = "cpu"
        """Name of device on which to run neural network model."""
        if torch.backends.mps.is_available():
            self.device = "mps"
        elif torch.cuda.is_available():
            self.device = "cuda"

    def __call__(self, input_img: Image.Image) -> Image.Image:
        """Process an image.

        Arguments:
            input_img: Input image
        Returns:
            Processed output image
        """
        input_img, output_mode = validate_image_and_convert_mode(
            input_img, self.inputs()["input"], "RGB"
        )

        input_arr = np.array(input_img)

        output_arr = self.upscale(input_arr)
        output_img = Image.fromarray(output_arr)
        if output_img.mode != output_mode:
            output_img = output_img.convert(output_mode)

        return output_img

    def __repr__(self) -> str:
        """Representation."""
        return f"{self.__class__.__name__}(model_input_path={self.model_input_path!r})"

    def upscale(self, input_arr: np.ndarray) -> np.ndarray:
        """Upscale an image array.

        Arguments:
            input_arr: Array to upscale
        Returns:
            Upscaled array
        """
        input_arr = input_arr * 1.0 / 255
        input_arr = np.transpose(input_arr[:, :, [2, 1, 0]], (2, 0, 1))
        input_tensor = torch.from_numpy(input_arr)
        input_tensor = input_tensor.float().unsqueeze(0).to(self.device)

        output_tensor = self.model(input_tensor).data.squeeze().float().cpu()
        output_arr: np.ndarray = output_tensor.clamp_(0, 1).numpy()
        output_arr = np.transpose(output_arr[[2, 1, 0], :, :], (1, 2, 0))
        output_arr = np.array(output_arr * 255, np.uint8)

        return output_arr

    @classmethod
    def inputs(cls) -> dict[str, tuple[ImageMode, ...]]:
        """Inputs to this operator."""
        return {
            "input": ("1", "L", "RGB"),
        }

    @classmethod
    def outputs(cls) -> dict[str, tuple[ImageMode, ...]]:
        """Outputs of this operator."""
        return {
            "output": ("1", "L", "RGB"),
        }
