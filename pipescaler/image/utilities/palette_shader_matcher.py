#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Matches image palettes globally or locally using a WGSL compute shader."""

from __future__ import annotations

from functools import lru_cache
from importlib import import_module
from logging import warning
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from pipescaler.image.core.enums import PaletteMatchMode
from pipescaler.image.core.exceptions import UnsupportedImageModeError
from pipescaler.image.core.functions import get_palette
from pipescaler.image.core.validation import validate_image_scale

__all__ = [
    "PaletteShaderError",
    "PaletteShaderExecutionError",
    "PaletteShaderMatcher",
    "PaletteShaderUnavailableError",
]


class PaletteShaderError(RuntimeError):
    """Base error for palette shader matching failures."""


class PaletteShaderUnavailableError(PaletteShaderError):
    """Raised when the shader runtime is unavailable."""


class PaletteShaderExecutionError(PaletteShaderError):
    """Raised when shader execution fails."""


class PaletteShaderMatcher:
    """Matches image palettes with exact integer GPU distance comparisons.

    wgpu selects the native backend automatically, including Metal on macOS.
    Both matching modes attempt GPU execution regardless of image or palette size.
    """

    _max_local_range = 2_147_483_647
    """Maximum local range representable as signed 32-bit integer."""
    _workgroup_x = 8
    """Shader workgroup width."""
    _workgroup_y = 8
    """Shader workgroup height."""
    _palette_batch_size = 65_536
    """Maximum unique target colors dispatched per basic-matching batch."""

    @classmethod
    def run(
        cls,
        ref_img: Image.Image,
        fit_img: Image.Image,
        local_range: int = 1,
        *,
        palette_match_mode: PaletteMatchMode = PaletteMatchMode.BASIC,
    ) -> Image.Image:
        """Match image colors to the full reference palette or local neighborhoods.

        Arguments:
            ref_img: image whose palette to use as reference
            fit_img: image whose palette to fit to reference
            local_range: range of adjacent pixels from which to draw best-fit color
            palette_match_mode: global or local reference color selection
        Returns:
            image with palette-matched colors
        Raises:
            UnsupportedImageModeError: if input modes differ or are unsupported
            ValueError: if images are empty, the mode is invalid, or local geometry
              or the local range is unsupported
            PaletteShaderError: if the compute runtime is unavailable or execution fails
        """
        if ref_img.mode != fit_img.mode:
            raise UnsupportedImageModeError(
                f"Image mode '{ref_img.mode}' of reference image does not match mode "
                f"'{fit_img.mode}' of fit image"
            )
        if fit_img.mode not in {"L", "RGB"}:
            raise UnsupportedImageModeError(
                f"Palette shader matcher supports 'L' and 'RGB', not '{fit_img.mode}'"
            )
        palette_match_mode = PaletteMatchMode(palette_match_mode)
        if palette_match_mode == PaletteMatchMode.LOCAL:
            normalized_local_range = cls._normalize_local_range(local_range)
            validate_image_scale(ref_img, fit_img, min_scale=2)
            normalized_local_range = min(normalized_local_range, max(ref_img.size))
        else:
            if min(*ref_img.size, *fit_img.size) == 0:
                raise ValueError("Palette matching requires nonempty images")
            normalized_local_range = 0

        channels = 1 if fit_img.mode == "L" else 3
        fit_arr = np.asarray(fit_img).reshape(fit_img.height, fit_img.width, channels)
        if palette_match_mode == PaletteMatchMode.BASIC:
            # Match unique target colors against the ordered, deduplicated reference
            ref_arr = get_palette(ref_img).astype(np.uint8).reshape(1, -1, channels)
            if channels == 1:
                colors, inverse = np.unique(fit_arr, return_inverse=True)
                queries = colors[:, np.newaxis]
            else:
                values = fit_arr.astype(np.uint32)
                packed = (
                    (values[:, :, 0] << 16) | (values[:, :, 1] << 8) | values[:, :, 2]
                )
                colors, inverse = np.unique(packed, return_inverse=True)
                queries = np.stack(
                    (colors >> 16, (colors >> 8) & 255, colors & 255), axis=-1
                ).astype(np.uint8)
            matched = np.empty_like(queries)
            for start in range(0, len(queries), cls._palette_batch_size):
                batch = queries[start : start + cls._palette_batch_size]
                matched[start : start + len(batch)] = cls._run_shader(
                    ref_arr=ref_arr,
                    fit_arr=batch[np.newaxis, :, :],
                    local_range=0,
                )[0]
            output_arr = matched[inverse].reshape(fit_arr.shape)
        else:
            ref_arr = np.asarray(ref_img).reshape(
                ref_img.height, ref_img.width, channels
            )
            output_arr = cls._run_shader(
                ref_arr=ref_arr,
                fit_arr=fit_arr,
                local_range=normalized_local_range,
            )
        if channels == 1:
            return Image.fromarray(output_arr[:, :, 0])
        return Image.fromarray(output_arr)

    @classmethod
    @lru_cache(maxsize=1)
    def _get_shader_source(cls) -> str:
        """Read and cache the WGSL source for palette matching.

        Returns:
            shader source text with workgroup placeholders
        """
        shader_path = Path(__file__).with_name("palette_match.wgsl")
        return shader_path.read_text(encoding="utf-8")

    @classmethod
    def _import_compute_with_buffers(cls) -> Any:
        """Import the wgpu compute helper.

        Returns:
            compute callback
        Raises:
            PaletteShaderUnavailableError: if the runtime cannot be imported
        """
        try:
            import_module("wgpu.backends.auto")
            compute_module = import_module("wgpu.utils.compute")
            compute_with_buffers = compute_module.compute_with_buffers
        except ModuleNotFoundError as exc:
            raise PaletteShaderUnavailableError("wgpu runtime not installed") from exc
        except (ImportError, OSError, RuntimeError) as exc:
            raise PaletteShaderUnavailableError(
                "wgpu runtime could not be loaded"
            ) from exc
        return compute_with_buffers

    @classmethod
    def _normalize_local_range(cls, local_range: int) -> int:
        """Normalize local range for transfer into WGSL params buffer.

        Arguments:
            local_range: range of adjacent pixels from which to draw best-fit color
        Returns:
            positive local range clamped to signed 32-bit integer max
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
                f"PaletteShaderMatcher: local_range {local_range_int} exceeds "
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
            ref_arr: reference image array with shape `(height, width, channels)`
            fit_arr: fit image array with shape `(height, width, channels)`
            local_range: reference neighborhood radius, or zero for the full palette
        Returns:
            matched image array with shape matching `fit_arr`
        Raises:
            PaletteShaderExecutionError: if shader execution fails
        """
        compute_with_buffers = cls._import_compute_with_buffers()
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
        workgroup_y = 1 if local_range == 0 else cls._workgroup_y
        workgroups_y = (fit_height + workgroup_y - 1) // workgroup_y

        shader = (
            cls._get_shader_source()
            .replace("WGX", str(cls._workgroup_x))
            .replace("WGY", str(workgroup_y))
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
            raise PaletteShaderExecutionError(
                f"wgpu compute shader execution failed: {exc}"
            ) from exc

        output_flat = np.frombuffer(result[3], dtype=np.uint32, count=fit_flat.size)
        output_arr = (
            np.clip(output_flat, 0, 255).astype(np.uint8).reshape(fit_arr.shape)
        )
        return output_arr
