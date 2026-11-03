#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Processes image using Pytorch models loaded through Spandrel."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import torch
from PIL import Image
from spandrel import ImageModelDescriptor, ModelLoader

from pipescaler.common.validation import val_float, val_input_path, val_int, val_str
from pipescaler.image.core.functions import RESAMPLE_METHODS, resize_float
from pipescaler.image.core.operators import ImageProcessor
from pipescaler.image.core.typing import ImageMode
from pipescaler.image.core.validation import validate_image_and_convert_mode
from pipescaler.image.subdivided_image import SubdividedImage

__all__ = ["SpandrelProcessor"]


class SpandrelProcessor(ImageProcessor):
    """Run RGB Spandrel models with explicit device and precision settings.

    Pillow calls and `upscale` accept 8-bit images. `upscale_float` accepts and
    returns normalized floating-point RGB arrays without 8-bit quantization.

    Tiling retains one tile on the device and accumulates the native-scale image
    on CPU. The model is loaded once and reused across calls. Transformer context
    can differ between tiled and full-frame inference; overlap reduces seams but
    does not guarantee identical results. Final resizing occurs after blending.
    """

    precision_dtypes = {
        "float32": torch.float32,
        "float16": torch.float16,
        "bfloat16": torch.bfloat16,
    }
    """Supported precision names and their corresponding tensor dtypes."""

    def __init__(  # noqa: PLR0913
        self,
        model_input_path: Path | str,
        *,
        device: str = "auto",
        precision: str = "float32",
        tile_size: int | None = None,
        tile_overlap: int = 0,
        target_scale: float | None = None,
        target_size: tuple[int, int] | None = None,
        resample: str = "lanczos",
    ):
        """Load an RGB model and select its execution device and precision.

        Arguments:
            model_input_path: path to a Spandrel-supported model checkpoint
            device: `auto`, `cpu`, `cuda`, `cuda:N`, `mps`, or `mps:0`; automatic
                selection prefers MPS, then CUDA, then CPU
            precision: `float32`, `float16`, or `bfloat16`; the model must support
                the requested precision, with no implicit fallback
            tile_size: maximum input tile width/height, at least 4 pixels, or
                `None` for full-frame inference; Spandrel may pad tiles internally
            tile_overlap: input pixels shared by tiles; nonnegative and smaller
                than tile_size, or zero when tiling is disabled
            target_scale: positive final scale relative to the input, or `None`
            target_size: final `(width, height)` in pixels; excludes target_scale
            resample: final resize filter; defaults to antialiased Lanczos
        Raises:
            ValueError: if the model is not an RGB image model, the device is
                unsupported or unavailable, or the precision is unsupported
            RuntimeError: if PyTorch cannot place the model on the requested
                device or execute the selected precision
        """
        super().__init__()

        self.model_input_path = val_input_path(model_input_path)
        """Path to model file."""
        self.tile_size = None if tile_size is None else val_int(tile_size, min_value=4)
        """Maximum input tile dimension, before model-required padding."""
        self.tile_overlap = val_int(tile_overlap, min_value=0)
        """Overlap between tiles in input pixels."""
        if (self.tile_size is None and self.tile_overlap) or (
            self.tile_size is not None and self.tile_overlap >= self.tile_size
        ):
            raise ValueError(
                "Tile overlap requires tiling and must be smaller than tile size"
            )
        if target_size is not None and target_scale is not None:
            raise ValueError("Choose either target_size or target_scale")
        self.target_scale = (
            None
            if target_scale is None
            else val_float(target_scale, min_value=0, min_exclusive=True, finite=True)
        )
        """Final scale relative to the original input, if selected."""
        if target_size is not None and len(target_size) != 2:
            raise ValueError("Target size must contain width and height")
        self.target_size = (
            None
            if target_size is None
            else (
                val_int(target_size[0], min_value=1),
                val_int(target_size[1], min_value=1),
            )
        )
        """Explicit final output dimensions in pixels, if selected."""
        self.resample = val_str(resample, options=RESAMPLE_METHODS)
        """Floating-point final resize filter."""
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
            f"device={str(self.device)!r}, precision={self.precision!r}, "
            f"tile_size={self.tile_size!r}, tile_overlap={self.tile_overlap!r}, "
            f"target_scale={self.target_scale!r}, target_size={self.target_size!r}, "
            f"resample={self.resample!r})"
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
        height, width = input_arr.shape[:2]
        if self.tile_size is None:
            output = self._infer_float(input_arr)
        else:
            boxes = SubdividedImage.get_boxes(
                width, height, self.tile_size, self.tile_overlap
            )
            scale = self.model.scale
            output = SubdividedImage.recompose_float(
                (
                    self._infer_float(input_arr[top:bottom, left:right], scale)
                    for left, top, right, bottom in boxes
                ),
                boxes * scale,
                self.tile_size * scale,
                self.tile_overlap * scale,
            )
        size = self.target_size
        if self.target_scale is not None:
            size = (round(width * self.target_scale), round(height * self.target_scale))
        if size is not None and size != (output.shape[1], output.shape[0]):
            output = resize_float(output, size, self.resample)
        return np.ascontiguousarray(np.clip(output, 0, 1), dtype=np.float32)

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

    def _infer_float(
        self, input_arr: np.ndarray, scale: int | None = None
    ) -> np.ndarray:
        """Infer one tile and return CPU floats without intermediate clipping.

        Arguments:
            input_arr: normalized floating-point RGB tile
            scale: native output scale to validate when reconstructing tiles
        Returns:
            unclipped HWC float32 model output on CPU
        Raises:
            ValueError: if a tile output does not match its native-scale geometry
        """
        input_tensor = (
            torch.from_numpy(np.array(input_arr, dtype=np.float32, copy=True))
            .permute(2, 0, 1)
            .unsqueeze(0)
            .to(device=self.device, dtype=self.dtype)
        )
        output = self._run_model(self.model, input_tensor)
        if scale is not None and output.shape[1:] != (
            input_arr.shape[0] * scale,
            input_arr.shape[1] * scale,
        ):
            raise ValueError("Model tile output does not match its native scale")
        return output.permute(1, 2, 0).contiguous().numpy()

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
