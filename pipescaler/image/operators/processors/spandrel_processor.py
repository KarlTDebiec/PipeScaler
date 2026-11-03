#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Processes image using Pytorch models loaded through Spandrel."""

from __future__ import annotations

from logging import warning
from pathlib import Path
from typing import Any, cast

import numpy as np
import torch
from PIL import Image
from spandrel import ModelLoader

from pipescaler.common.validation import val_input_path
from pipescaler.image.core.operators import ImageProcessor
from pipescaler.image.core.typing import ImageMode
from pipescaler.image.core.validation import validate_image_and_convert_mode

__all__ = ["SpandrelProcessor"]


class SpandrelProcessor(ImageProcessor):
    """Processes image using Pytorch models loaded through Spandrel."""

    def __init__(self, model_input_path: Path | str, **kwargs: Any):
        """Initialize.

        Arguments:
            model_input_path: Path to model file
            **kwargs: Additional keyword arguments (reserved for future use)
        Raises:
            ValueError: if the model descriptor does not support RGB input and output
        """
        super().__init__()

        self.device = "cpu"
        """Name of device on which to run neural network model."""
        if torch.backends.mps.is_available():
            self.device = "mps"
        elif torch.cuda.is_available():
            self.device = "cuda"

        self.model_input_path = val_input_path(model_input_path)
        """Path to model file."""
        self.model = ModelLoader().load_from_file(self.model_input_path)
        """Neural network model."""
        if self.model.input_channels != 3 or self.model.output_channels != 3:
            raise ValueError(
                "Spandrel models must have 3 input and 3 output channels for RGB "
                "processing; descriptor reports "
                f"input_channels={self.model.input_channels}, "
                f"output_channels={self.model.output_channels}"
            )

        self.model.eval()
        try:
            self.model = self.model.to(self.device)
        except AssertionError as exc:
            # Fallback to CPU (seen occasionally with MPS for some layers)
            self.device = "cpu"
            self.model = self.model.to(self.device)
            warning(
                f"{self.__class__.__name__}: Torch raised '{exc}' on device placement; "
                "falling back to CPU."
            )

    def __repr__(self) -> str:
        """Representation.

        Returns:
            string representation of this object
        """
        model_input_path = f"Path({str(self.model_input_path)!r})"
        return f"{self.__class__.__name__}(model_input_path={model_input_path})"

    def __call__(self, input_image: Image.Image) -> Image.Image:
        """Process an image.

        Arguments:
            input_image: Input image
        Returns:
            Processed output image
        Raises:
            ValueError: if the model output is not a single-image RGB tensor
        """
        input_img, output_mode = validate_image_and_convert_mode(
            input_image, self.inputs()["input"], "RGB"
        )

        output_arr = self.upscale(np.array(input_img))
        output_img = Image.fromarray(output_arr)
        if output_img.mode != output_mode:
            output_img = output_img.convert(output_mode)

        return output_img

    def upscale(self, input_arr: np.ndarray) -> np.ndarray:
        """Upscale an image array.

        Arguments:
            input_arr: Array to upscale
        Returns:
            Upscaled array
        Raises:
            ValueError: if the input array or model output has an invalid shape
        """
        self._validate_rgb_array(input_arr, "input")
        input_arr = input_arr * 1.0 / 255
        input_arr = np.transpose(input_arr[:, :, [2, 1, 0]], (2, 0, 1))
        input_tensor = torch.from_numpy(input_arr)
        input_tensor = input_tensor.float().unsqueeze(0).to(self.device)

        model = cast(Any, self.model)
        output_tensor = self._run_model(model, input_tensor)
        output_arr: np.ndarray = output_tensor.clamp_(0, 1).numpy()
        output_arr = np.transpose(output_arr[[2, 1, 0], :, :], (1, 2, 0))
        output_arr = np.array(output_arr * 255, np.uint8)

        return output_arr

    @classmethod
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links.

        Returns:
            Markdown help describing this component
        """
        return (
            "Processes image using Pytorch models loaded through "
            "[Spandrel](https://github.com/chaiNNer-org/spandrel)."
        )

    @classmethod
    def inputs(cls) -> dict[str, tuple[ImageMode, ...]]:
        """Inputs to this operator.

        Returns:
            mapping of input names to their supported image modes
        """
        return {
            "input": ("1", "L", "RGB"),
        }

    @classmethod
    def outputs(cls) -> dict[str, tuple[ImageMode, ...]]:
        """Outputs of this operator.

        Returns:
            mapping of output names to their supported image modes
        """
        return {
            "output": ("1", "L", "RGB"),
        }

    @staticmethod
    def _run_model(model: Any, input_tensor: torch.Tensor) -> torch.Tensor:
        """Run a model and validate its single-image RGB tensor output.

        Arguments:
            model: loaded Spandrel model
            input_tensor: BCHW RGB tensor
        Returns:
            validated output image as a CHW tensor
        Raises:
            ValueError: if the model output is not a single-image RGB tensor
        """
        output = model(input_tensor)
        if not isinstance(output, torch.Tensor):
            raise ValueError("Model output must be a PyTorch tensor")
        if output.ndim != 4 or output.shape[0] != 1 or output.shape[1] != 3:
            raise ValueError(
                "Model output must have shape (1, 3, height, width); "
                f"got {tuple(output.shape)}"
            )
        if output.shape[2] < 1 or output.shape[3] < 1:
            raise ValueError("Model output must have non-empty spatial dimensions")
        return output[0].detach().float().cpu()

    @staticmethod
    def _validate_rgb_array(image_arr: np.ndarray, label: str):
        """Validate an RGB image array before converting it to a tensor.

        Arguments:
            image_arr: image data to validate
            label: role of the image in the model call
        Raises:
            ValueError: if the array is not a non-empty HWC RGB image
        """
        if image_arr.ndim != 3 or image_arr.shape[2] != 3:
            raise ValueError(
                f"Model {label} must be an HWC RGB array; got shape {image_arr.shape}"
            )
        if image_arr.shape[0] < 1 or image_arr.shape[1] < 1:
            raise ValueError(f"Model {label} must have non-empty spatial dimensions")
