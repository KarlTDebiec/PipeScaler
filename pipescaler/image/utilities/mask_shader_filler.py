#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Fills masked image pixels with an iterative WGSL compute pipeline."""

from __future__ import annotations

from functools import lru_cache
from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
from PIL import Image

from pipescaler.image.core.exceptions import UnsupportedImageModeError

if TYPE_CHECKING:
    from wgpu import GPUBindGroupLayout, GPUComputePipeline, GPUDevice

__all__ = ["MaskShaderError", "MaskShaderFiller"]


class MaskShaderError(RuntimeError):
    """Raised when the mask-filling compute runtime is unavailable or fails."""


class MaskShaderFiller:
    """Fill pixels with the highest unmasked-neighbor count in each round.

    Counts and integer color averages are computed from the previous round before
    any pixels are filled. Pipelines are cached, and per-image buffers remain on
    the device across batches of rounds. Fully masked images remain unchanged.
    """

    _rounds_per_batch = 32
    """Number of fill rounds submitted between progress readbacks."""
    _workgroup_size = 8
    """Width and height of each image-processing workgroup."""

    @classmethod
    def run(cls, img: Image.Image, mask: Image.Image) -> Image.Image:
        """Fill an image with exact integer averages of unmasked neighbors.

        Arguments:
            img: grayscale or RGB image to fill
            mask: same-sized mode 1 image whose white pixels are masked
        Returns:
            image with masked pixels filled, preserving the input mode and size
        Raises:
            UnsupportedImageModeError: if the image or mask mode is unsupported
            ValueError: if image and mask sizes differ
            MaskShaderError: if the compute runtime cannot load or execution fails
        """
        if img.mode not in {"L", "RGB"} or mask.mode != "1":
            raise UnsupportedImageModeError(
                "Mask filling requires an L or RGB image and a mode 1 mask; "
                f"received '{img.mode}' and '{mask.mode}'"
            )
        if img.size != mask.size:
            raise ValueError("Mask filling requires matching image and mask sizes")

        mask_arr = np.asarray(mask, dtype=np.uint32)
        masked_count = int(np.count_nonzero(mask_arr))
        if masked_count in {0, mask_arr.size}:
            return img.copy()
        image_arr = np.asarray(img, dtype=np.uint32)
        if img.mode == "RGB":
            pixels = (
                image_arr[:, :, 0]
                | (image_arr[:, :, 1] << 8)
                | (image_arr[:, :, 2] << 16)
            )
        else:
            pixels = image_arr

        try:
            output = cls._run_shader(pixels, mask_arr, masked_count)
        except MaskShaderError:
            raise
        except Exception as exc:  # pragma: no cover - runtime specific
            raise MaskShaderError(
                f"Mask-filling shader execution failed: {exc}"
            ) from exc
        if img.mode == "RGB":
            output = np.stack(
                (output & 255, (output >> 8) & 255, (output >> 16) & 255), axis=-1
            )
        return Image.fromarray(output.astype(np.uint8))

    @classmethod
    @lru_cache(maxsize=1)
    def _get_runtime(
        cls,
    ) -> tuple[GPUDevice, GPUBindGroupLayout, tuple[GPUComputePipeline, ...]]:
        """Load the compute device and compile the three cached entry points.

        Returns:
            device, shared binding layout, and reset/count/fill pipelines
        Raises:
            MaskShaderError: if the runtime or shader cannot load
        """
        try:
            device = import_module("wgpu.utils").get_default_device()
            shader = device.create_shader_module(
                code=Path(__file__)
                .with_name("mask_fill.wgsl")
                .read_text(encoding="utf-8")
                .replace("WGX", str(cls._workgroup_size))
                .replace("WGY", str(cls._workgroup_size))
            )
            binding_layout = device.create_bind_group_layout(
                entries=[
                    {
                        "binding": binding,
                        "visibility": "COMPUTE",
                        "buffer": {
                            "type": "read-only-storage" if binding == 4 else "storage"
                        },
                    }
                    for binding in range(5)
                ]
            )
            pipeline_layout = device.create_pipeline_layout(
                bind_group_layouts=[binding_layout]
            )
            pipelines = tuple(
                device.create_compute_pipeline(
                    layout=pipeline_layout,
                    compute={"module": shader, "entry_point": entry_point},
                )
                for entry_point in ("reset", "count_neighbors", "fill")
            )
        except Exception as exc:
            raise MaskShaderError(
                f"Mask-filling runtime could not load: {exc}"
            ) from exc
        return device, binding_layout, pipelines

    @classmethod
    def _run_shader(
        cls, pixels: np.ndarray, mask: np.ndarray, masked_count: int
    ) -> np.ndarray:
        """Execute batches of fill rounds without transferring image buffers.

        Arguments:
            pixels: packed grayscale or RGB pixel values
            mask: unsigned integer mask with one for masked pixels
            masked_count: number of pixels initially requiring filling
        Returns:
            packed filled pixels with the input array shape
        Raises:
            MaskShaderError: if filling fails to finish within the progress bound
        """
        device, binding_layout, pipelines = cls._get_runtime()
        height, width = mask.shape
        buffers = []
        try:
            for data, usage in (
                (pixels, "STORAGE|COPY_SRC"),
                (mask, "STORAGE"),
                (None, "STORAGE"),
                (np.zeros(1, dtype=np.uint32), "STORAGE|COPY_SRC"),
                (np.array([width, height], dtype=np.uint32), "STORAGE"),
            ):
                if data is None:
                    buffer = device.create_buffer(size=pixels.nbytes, usage=usage)
                else:
                    buffer = device.create_buffer_with_data(data=data, usage=usage)
                buffers.append(buffer)
            bindings = device.create_bind_group(
                layout=binding_layout,
                entries=[
                    {"binding": index, "resource": {"buffer": buffer}}
                    for index, buffer in enumerate(buffers)
                ],
            )
            workgroups_x = (width + cls._workgroup_size - 1) // cls._workgroup_size
            workgroups_y = (height + cls._workgroup_size - 1) // cls._workgroup_size
            # Every productive round fills at least one pixel; allow a final zero
            for start in range(0, masked_count + 1, cls._rounds_per_batch):
                encoder = device.create_command_encoder()
                compute_pass = encoder.begin_compute_pass()
                compute_pass.set_bind_group(0, bindings)
                rounds = min(cls._rounds_per_batch, masked_count + 1 - start)
                for _ in range(rounds):
                    for index, pipeline in enumerate(pipelines):
                        compute_pass.set_pipeline(pipeline)
                        if index == 0:
                            compute_pass.dispatch_workgroups(1)
                        else:
                            compute_pass.dispatch_workgroups(workgroups_x, workgroups_y)
                compute_pass.end()
                device.queue.submit([encoder.finish()])
                maximum = np.frombuffer(
                    device.queue.read_buffer(buffers[3]), dtype=np.uint32
                )[0]
                if maximum == 0:
                    output = np.frombuffer(
                        device.queue.read_buffer(buffers[0]), dtype=np.uint32
                    )
                    return output.reshape(pixels.shape).copy()
            raise MaskShaderError("Mask-filling shader exceeded its fill-round bound")
        finally:
            for buffer in buffers:
                buffer.destroy()
