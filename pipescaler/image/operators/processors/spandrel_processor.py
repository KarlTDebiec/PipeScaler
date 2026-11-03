#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Processes image using Pytorch models loaded through Spandrel."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import torch
from PIL import Image
from spandrel import ImageModelDescriptor, ModelLoader

from pipescaler.common.validation import val_input_path, val_str
from pipescaler.image.core.operators import ImageProcessor
from pipescaler.image.core.typing import ImageMode
from pipescaler.image.core.validation import validate_image_and_convert_mode

__all__ = ["SpandrelProcessor"]


class SpandrelProcessor(ImageProcessor):
    """Run RGB Spandrel models with explicit device and precision settings.

    Pillow calls and `upscale` accept 8-bit images. `upscale_float` accepts and
    returns normalized floating-point RGB arrays without 8-bit quantization.
    """

    precision_dtypes = {
        "float32": torch.float32,
        "float16": torch.float16,
        "bfloat16": torch.bfloat16,
    }
    """Supported precision names and their corresponding tensor dtypes."""

    def __init__(
        self,
        model_input_path: Path | str,
        *,
        device: str = "auto",
        precision: str = "float32",
    ):
        """Load an RGB model and select its execution device and precision.

        Arguments:
            model_input_path: path to a Spandrel-supported model checkpoint
            device: `auto`, `cpu`, `cuda`, `cuda:N`, `mps`, or `mps:0`; automatic
                selection prefers MPS, then CUDA, then CPU
            precision: `float32`, `float16`, or `bfloat16`; the model must support
                the requested precision, with no implicit fallback
        Raises:
            ValueError: if the model is not an RGB image model, the device is
                unsupported or unavailable, or the precision is unsupported
            RuntimeError: if PyTorch cannot place the model on the requested
                device or execute the selected precision
        """
        super().__init__()

        self.model_input_path = val_input_path(model_input_path)
        """Path to model file."""
        self.device = self._validate_device(device)
        """Selected execution device; explicitly requested devices never fall back."""
        self.precision = val_str(precision, options=self.precision_dtypes.keys())
        """Validated precision name."""
        self.dtype = self.precision_dtypes[self.precision]
        """Tensor dtype shared by model weights and inference input."""
        model = ModelLoader().load_from_file(self.model_input_path)
        if not isinstance(model, ImageModelDescriptor):
            raise ValueError("Spandrel processor requires an image-to-image model")
        if model.input_channels != 3 or model.output_channels != 3:
            raise ValueError(
                "Spandrel models must have 3 input and 3 output channels for RGB "
                "processing; descriptor reports "
                f"input_channels={model.input_channels}, "
                f"output_channels={model.output_channels}"
            )
        if (self.dtype == torch.float16 and not model.supports_half) or (
            self.dtype == torch.bfloat16 and not model.supports_bfloat16
        ):
            raise ValueError(
                f"Model architecture '{model.architecture.id}' does not support "
                f"precision '{self.precision}'"
            )
        self.model = model.to(device=self.device, dtype=self.dtype).eval()
        """RGB image model with weights matching the selected device and dtype."""

    def __call__(self, input_image: Image.Image) -> Image.Image:
        """Process an image.

        Arguments:
            input_image: input image
        Returns:
            processed output image
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

    def __repr__(self) -> str:
        """Representation.

        Returns:
            string representation of this object
        """
        model_input_path = f"Path({str(self.model_input_path)!r})"
        return (
            f"{self.__class__.__name__}(model_input_path={model_input_path}, "
            f"device={str(self.device)!r}, precision={self.precision!r})"
        )

    def upscale(self, input_arr: np.ndarray) -> np.ndarray:
        """Upscale an 8-bit HWC RGB array, rounding only the final output.

        Arguments:
            input_arr: non-empty uint8 RGB array with shape `(height, width, 3)`
        Returns:
            uint8 RGB array with the model's output dimensions
        Raises:
            ValueError: if the input has an invalid shape or model output is invalid
            TypeError: if the input dtype is not uint8
        """
        self._validate_rgb_array(input_arr, "input")
        if input_arr.dtype != np.uint8:
            raise TypeError(
                "upscale requires uint8 input; use upscale_float for floats"
            )
        output_arr = self.upscale_float(input_arr.astype(np.float32) / 255)
        return np.rint(output_arr * 255).astype(np.uint8)

    def upscale_float(self, input_arr: np.ndarray) -> np.ndarray:
        """Upscale normalized floating-point HWC RGB without quantizing to 8-bit.

        The input is copied before inference, so read-only and strided arrays are
        accepted without exposing caller-owned memory to model operations.

        Arguments:
            input_arr: non-empty floating-point RGB array with shape
                `(height, width, 3)` and finite values in `[0, 1]`
        Returns:
            contiguous float32 RGB array in `[0, 1]`, with the model's output
            dimensions and fractional values preserved
        Raises:
            TypeError: if the input dtype is not floating-point
            ValueError: if the input shape or values are invalid, or the model
                returns an invalid output
        """
        self._validate_rgb_array(input_arr, "input")
        if not np.issubdtype(input_arr.dtype, np.floating):
            raise TypeError("upscale_float requires floating-point input")
        if (
            not np.isfinite(input_arr).all()
            or input_arr.min() < 0
            or input_arr.max() > 1
        ):
            raise ValueError(
                "Floating-point input must contain finite values in [0, 1]"
            )
        input_tensor = (
            torch.from_numpy(np.array(input_arr, dtype=np.float32, copy=True))
            .permute(2, 0, 1)
            .unsqueeze(0)
            .to(device=self.device, dtype=self.dtype)
        )
        output_tensor = self._run_model(self.model, input_tensor)
        return output_tensor.clamp(0, 1).permute(1, 2, 0).contiguous().numpy()

    @classmethod
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links.

        Returns:
            markdown help describing this component
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
    def _run_model(
        model: ImageModelDescriptor, input_tensor: torch.Tensor
    ) -> torch.Tensor:
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
        output = output[0].detach().float().cpu()
        if not torch.isfinite(output).all():
            raise ValueError("Model output must contain only finite values")
        return output

    @staticmethod
    def _validate_device(device: str) -> torch.device:
        """Resolve automatic selection and reject unavailable execution devices.

        Arguments:
            device: requested execution device or `auto`
        Returns:
            supported, available PyTorch device
        Raises:
            ValueError: if the device is unsupported, unavailable, or out of range
        """
        if device == "auto":
            if torch.backends.mps.is_available():
                device = "mps"
            elif torch.cuda.is_available():
                device = "cuda"
            else:
                device = "cpu"
        try:
            selected = torch.device(device)
        except (RuntimeError, ValueError) as exc:
            raise ValueError(f"Invalid execution device: {device!r}") from exc
        if selected.type not in {"cpu", "cuda", "mps"}:
            raise ValueError(f"Unsupported execution device: {device!r}")
        if selected.type == "cpu" and selected.index is not None:
            raise ValueError("CPU execution does not accept a device index")
        if selected.type == "cuda":
            if not torch.cuda.is_available():
                raise ValueError("CUDA execution was requested but CUDA is unavailable")
            if (
                selected.index is not None
                and selected.index >= torch.cuda.device_count()
            ):
                raise ValueError(f"CUDA device index is unavailable: {selected.index}")
        if selected.type == "mps" and not torch.backends.mps.is_available():
            raise ValueError("MPS execution was requested but MPS is unavailable")
        if selected.type == "mps" and selected.index not in {None, 0}:
            raise ValueError(f"MPS device index is unavailable: {selected.index}")
        return selected

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
