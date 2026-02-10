#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Matches image palettes locally using a WGSL compute shader."""

from __future__ import annotations

from importlib import import_module
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

    _workgroup_x = 8
    _workgroup_y = 8

    _wgsl_shader = """
@group(0) @binding(0)
var<storage, read> fit_pixels: array<u32>;
@group(0) @binding(1)
var<storage, read> ref_pixels: array<u32>;
@group(0) @binding(2)
var<storage, read> params: array<u32>;
@group(0) @binding(3)
var<storage, read_write> output_pixels: array<u32>;

fn weighted_distance(
    fit_r_u: u32,
    fit_g_u: u32,
    fit_b_u: u32,
    ref_r_u: u32,
    ref_g_u: u32,
    ref_b_u: u32
) -> f32 {
    let fit_r = f32(fit_r_u);
    let fit_g = f32(fit_g_u);
    let fit_b = f32(fit_b_u);
    let ref_r = f32(ref_r_u);
    let ref_g = f32(ref_g_u);
    let ref_b = f32(ref_b_u);
    let rmean = (fit_r + ref_r) * 0.5;
    let dr = fit_r - ref_r;
    let dg = fit_g - ref_g;
    let db = fit_b - ref_b;
    return ((2.0 + (rmean / 256.0)) * (dr * dr))
        + (4.0 * (dg * dg))
        + ((2.0 + ((255.0 - rmean) / 256.0)) * (db * db));
}

@compute @workgroup_size(WGX, WGY, 1)
fn main(@builtin(global_invocation_id) gid: vec3<u32>) {
    let fit_height: u32 = params[0];
    let fit_width: u32 = params[1];
    let ref_height: u32 = params[2];
    let ref_width: u32 = params[3];
    let local_range: i32 = i32(params[4]);
    let channels: u32 = params[5];

    let x = gid.x;
    let y = gid.y;
    if (x >= fit_width || y >= fit_height) {
        return;
    }

    let fit_idx = (y * fit_width + x) * channels;
    let fit_r = fit_pixels[fit_idx];
    var fit_g = fit_r;
    var fit_b = fit_r;
    if (channels == 3u) {
        fit_g = fit_pixels[fit_idx + 1u];
        fit_b = fit_pixels[fit_idx + 2u];
    }

    let center_x_u: u32 = min((x * ref_width) / fit_width, ref_width - 1u);
    let center_y_u: u32 = min((y * ref_height) / fit_height, ref_height - 1u);
    let center_x: i32 = i32(center_x_u);
    let center_y: i32 = i32(center_y_u);

    let x_start = max(0, center_x - local_range);
    let x_end = min(i32(ref_width) - 1, center_x + local_range);
    let y_start = max(0, center_y - local_range);
    let y_end = min(i32(ref_height) - 1, center_y + local_range);

    var best_dist = 1e30;
    var best_r: u32 = fit_r;
    var best_g: u32 = fit_g;
    var best_b: u32 = fit_b;

    var ry = y_start;
    loop {
        if (ry > y_end) {
            break;
        }
        var rx = x_start;
        loop {
            if (rx > x_end) {
                break;
            }
            let ref_idx = (u32(ry) * ref_width + u32(rx)) * channels;
            let ref_r = ref_pixels[ref_idx];
            var ref_g = ref_r;
            var ref_b = ref_r;
            if (channels == 3u) {
                ref_g = ref_pixels[ref_idx + 1u];
                ref_b = ref_pixels[ref_idx + 2u];
            }

            var dist = 0.0;
            if (channels == 3u) {
                dist = weighted_distance(fit_r, fit_g, fit_b, ref_r, ref_g, ref_b);
            } else {
                let d = f32(i32(fit_r) - i32(ref_r));
                dist = d * d;
            }

            if (dist < best_dist) {
                best_dist = dist;
                best_r = ref_r;
                best_g = ref_g;
                best_b = ref_b;
            }

            rx = rx + 1;
        }
        ry = ry + 1;
    }

    output_pixels[fit_idx] = best_r;
    if (channels == 3u) {
        output_pixels[fit_idx + 1u] = best_g;
        output_pixels[fit_idx + 2u] = best_b;
    }
}
"""

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

        ref_arr, fit_arr = cls._prepare_arrays(ref_img, fit_img)
        channels = fit_arr.shape[2]
        output_arr = cls._run_shader(
            ref_arr=ref_arr,
            fit_arr=fit_arr,
            local_range=local_range,
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

        shader = cls._wgsl_shader.replace("WGX", str(cls._workgroup_x)).replace(
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
