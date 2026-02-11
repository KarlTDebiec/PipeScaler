#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Matches image palettes locally using a WGSL compute shader."""

from __future__ import annotations

from functools import lru_cache
from importlib import import_module
from logging import warning
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from pipescaler.image.core.exceptions import UnsupportedImageModeError


class LocalPaletteShaderError(RuntimeError):
    """Base error for local palette shader matching failures."""


class LocalPaletteShaderUnavailableError(LocalPaletteShaderError):
    """Raised when the shader runtime is unavailable."""


class LocalPaletteShaderExecutionError(LocalPaletteShaderError):
    """Raised when shader execution fails."""


class LocalPaletteShaderMatcher:
    """Matches image palettes locally using a WGSL compute shader."""

    _max_local_range = 2_147_483_647
    """Maximum local range representable as signed 32-bit integer."""
    _workgroup_x = 8
    _workgroup_y = 8

    @classmethod
    def run(
        cls, ref_img: Image.Image, fit_img: Image.Image, local_range: int = 1
    ) -> Image.Image:
        """Match an image palette to nearby reference colors using a shader.

        Arguments:
            ref_img: Image whose palette to use as reference
            fit_img: Image whose palette to fit to reference
            local_range: Range of adjacent pixels from which to draw best-fit color
        Returns:
            Image with locally palette-matched colors
        """
        if ref_img.mode != fit_img.mode:
            raise UnsupportedImageModeError(
                f"Image mode '{ref_img.mode}' of reference image does not match mode "
                f"'{fit_img.mode}' of fit image"
            )
        if fit_img.mode not in {"L", "RGB"}:
            raise UnsupportedImageModeError(
                f"Local palette shader matcher supports 'L' and 'RGB', not "
                f"'{fit_img.mode}'"
            )
        normalized_local_range = cls._normalize_local_range(local_range)

        ref_arr, fit_arr = cls._prepare_arrays(ref_img, fit_img)
        channels = fit_arr.shape[2]
        output_arr = cls._run_shader(
            ref_arr=ref_arr,
            fit_arr=fit_arr,
            local_range=normalized_local_range,
        )
        if channels == 1:
            return Image.fromarray(output_arr[:, :, 0])
        return Image.fromarray(output_arr)

    @classmethod
    def _get_compute_with_buffers(cls) -> Any:
        """Get the ``compute_with_buffers`` helper from wgpu."""
        try:
            import_module("wgpu.backends.auto")
            compute_module = import_module("wgpu.utils.compute")
            compute_with_buffers = compute_module.compute_with_buffers
        except ModuleNotFoundError as exc:
            raise LocalPaletteShaderUnavailableError(
                "wgpu runtime not installed"
            ) from exc
        except ImportError as exc:
            raise LocalPaletteShaderUnavailableError(
                "wgpu runtime could not be imported"
            ) from exc
        return compute_with_buffers

    @classmethod
    def _prepare_arrays(
        cls, ref_img: Image.Image, fit_img: Image.Image
    ) -> tuple[np.ndarray, np.ndarray]:
        """Convert input images into channel-last arrays for shader execution.

        Arguments:
            ref_img: Image whose palette to use as reference
            fit_img: Image whose palette to fit to reference
        Returns:
            Reference and fit arrays with shape ``(height, width, channels)``
        """
        ref_arr = np.array(ref_img, np.uint8)
        fit_arr = np.array(fit_img, np.uint8)
        if fit_img.mode == "L":
            ref_arr = ref_arr[:, :, np.newaxis]
            fit_arr = fit_arr[:, :, np.newaxis]
        return ref_arr, fit_arr

    @classmethod
    def _normalize_local_range(cls, local_range: int) -> int:
        """Normalize local range for transfer into WGSL params buffer.

        Arguments:
            local_range: range of adjacent pixels from which to draw best-fit color
        Returns:
            non-negative local range clamped to signed 32-bit integer max
        Raises:
            ValueError: if local_range is not an integer >= 1
        """
        try:
            local_range_int = int(local_range)
        except (TypeError, ValueError) as exc:
            raise ValueError("local_range must be an integer") from exc
        if local_range_int < 1:
            raise ValueError("local_range must be >= 1")
        if local_range_int > cls._max_local_range:
            warning(
                f"LocalPaletteShaderMatcher: local_range {local_range_int} exceeds "
                f"{cls._max_local_range}; clamping"
            )
            local_range_int = cls._max_local_range
        return local_range_int

    @classmethod
    def _run_shader(
        cls, *, ref_arr: np.ndarray, fit_arr: np.ndarray, local_range: int
    ) -> np.ndarray:
        """Execute the compute shader and return matched pixels.

        Arguments:
            ref_arr: Reference image array with shape ``(height, width, channels)``
            fit_arr: Fit image array with shape ``(height, width, channels)``
            local_range: Range of adjacent pixels from which to draw best-fit color
        Returns:
            Matched image array with shape matching ``fit_arr``
        """
        compute_with_buffers = cls._get_compute_with_buffers()
        fit_height, fit_width, channels = fit_arr.shape
        ref_height, ref_width, _ = ref_arr.shape

        fit_flat = np.ascontiguousarray(fit_arr.reshape(-1), dtype=np.uint32)
        ref_flat = np.ascontiguousarray(ref_arr.reshape(-1), dtype=np.uint32)
        params = np.array(
            [fit_height, fit_width, ref_height, ref_width, local_range, channels],
            dtype=np.uint32,
        )
        output_size_bytes = fit_flat.nbytes

        workgroups_x = (fit_width + cls._workgroup_x - 1) // cls._workgroup_x
        workgroups_y = (fit_height + cls._workgroup_y - 1) // cls._workgroup_y

        shader = cls._get_shader_source().replace("WGX", str(cls._workgroup_x)).replace(
            "WGY", str(cls._workgroup_y)
        )
        try:
            result = compute_with_buffers(
                input_arrays={
                    0: fit_flat,
                    1: ref_flat,
                    2: params,
                },
                output_arrays={3: output_size_bytes},
                shader=shader,
                n=(workgroups_x, workgroups_y, 1),
            )
        except Exception as exc:  # pragma: no cover - runtime specific
            raise LocalPaletteShaderExecutionError(
                f"wgpu compute shader execution failed: {exc}"
            ) from exc

        output_flat = np.frombuffer(result[3], dtype=np.uint32, count=fit_flat.size)
        output_arr = (
            np.clip(output_flat, 0, 255).astype(np.uint8).reshape(fit_arr.shape)
        )
        return output_arr

    @classmethod
    @lru_cache(maxsize=1)
    def _get_shader_source(cls) -> str:
        """Read and cache the WGSL source for local palette matching.

        Returns:
            shader source text with workgroup placeholders
        """
        shader_path = Path(__file__).with_name("local_palette_match.wgsl")
        return shader_path.read_text(encoding="utf-8")
