#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Erases masked pixels within an image."""

from __future__ import annotations

from functools import lru_cache
from importlib import import_module
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
from PIL import Image

from pipescaler.core import Utility
from pipescaler.core.exceptions import PipeScalerError
from pipescaler.image.core.enums import MaskFillMode
from pipescaler.image.core.exceptions import UnsupportedImageModeError

from .palette_matcher import PaletteMatcher

if TYPE_CHECKING:
    from wgpu import GPUBindGroupLayout, GPUComputePipeline, GPUDevice

__all__ = ["MaskFillError", "MaskFiller"]

logger = getLogger(__name__)


class MaskFillError(PipeScalerError, RuntimeError):
    """Raised when the mask-filling compute runtime is unavailable or fails."""


class MaskFiller(Utility):
    """Erase masked pixels, preferring WGSL for substantial masked regions.

    Masks below 1,024 masked pixels use the CPU to avoid dispatch overhead.
    Larger masks use cached compute pipelines and fall back to the CPU if the
    graphics runtime fails. The first GPU fill also initializes the runtime.
    """

    _minimum_shader_pixels = 1024
    """Minimum masked-pixel count before attempting GPU execution."""
    _rounds_per_batch = 32
    """Number of fill rounds submitted between progress readbacks."""
    _workgroup_size = 8
    """Width and height of each image-processing workgroup."""

    @classmethod
    def run(  # ty: ignore[invalid-method-override]
        cls, img: Image.Image, mask: Image.Image, mask_fill_mode: MaskFillMode
    ) -> Image.Image:
        """Erases masked pixels within an image.

        Each round fills only pixels with the highest unmasked-neighbor count,
        using integer averages from the previous round's 3x3 neighborhoods.
        Fully masked images remain unchanged because no color can propagate.

        Arguments:
            img: image whose mode must be L or RGB
            mask: same-sized mode 1 mask; white pixels are masked
            mask_fill_mode: whether to match filled colors to the original palette
        Returns:
            image with masked pixels replaced
        Raises:
            UnsupportedImageModeError: if the image or mask mode is unsupported
            ValueError: if image and mask sizes differ
        """
        if img.mode not in {"L", "RGB"} or mask.mode != "1":
            raise UnsupportedImageModeError(
                "Mask filling requires an L or RGB image and a mode 1 mask; "
                f"received '{img.mode}' and '{mask.mode}'"
            )
        if img.size != mask.size:
            raise ValueError("Mask filling requires matching image and mask sizes")
        mask_arr = np.asarray(mask)
        masked_count = int(np.count_nonzero(mask_arr))
        if masked_count in {0, mask_arr.size}:
            return img.copy()

        filled_img = None
        if masked_count >= cls._minimum_shader_pixels:
            try:
                filled_img = cls._run_gpu(img, mask_arr, masked_count)
            except MaskFillError as exc:
                logger.warning(
                    f"{cls.__name__}: Shader path unavailable ('{exc}'); "
                    "falling back to CPU mask filling."
                )

        if filled_img is None:
            image_arr = np.array(img)
            # Get all pixels to be filled
            pixels_to_fill = set()
            for x in range(mask_arr.shape[0]):
                for y in range(mask_arr.shape[1]):
                    if mask_arr[x, y]:
                        pixels_to_fill.add((x, y))

            # Iterate until no pixels remain to be filled
            opaque_neighbor_counts: dict[tuple[int, int], int] = {}
            pixels_to_recount = pixels_to_fill.copy()
            while len(pixels_to_fill) > 0:
                (
                    image_arr,
                    pixels_to_fill,
                    opaque_neighbor_counts,
                    pixels_to_recount,
                ) = cls.run_iteration(
                    image_arr, pixels_to_fill, opaque_neighbor_counts, pixels_to_recount
                )
            filled_img = Image.fromarray(image_arr)

        if mask_fill_mode == MaskFillMode.MATCH_PALETTE:
            filled_img = PaletteMatcher.run(img, filled_img)
        return filled_img

    @staticmethod
    def run_iteration(
        image_arr: np.ndarray,
        pixels_to_fill: set[tuple[int, int]],
        opaque_neighbor_counts: dict[tuple[int, int], int],
        pixels_to_recount: set[tuple[int, int]],
    ) -> tuple[
        np.ndarray,
        set[tuple[int, int]],
        dict[tuple[int, int], int],
        set[tuple[int, int]],
    ]:
        """Fills pixels whose number of opaque neighbors is equal to the max.

        Arguments:
            image_arr: Image array
            pixels_to_fill: Pixels that remain to be filled
            opaque_neighbor_counts: number of opaque neighbors of each pixel to fill
            pixels_to_recount: Pixels whose opaque neighbor counts need to be updated
        Returns:
            Updated image array, pixels to fill, opaque neighbor counts, and pixels to
            recount
        """
        width = image_arr.shape[0]
        height = image_arr.shape[1]

        # Count number of opaque pixels adjacent to each pixel to be filled
        for pixel in pixels_to_recount:
            count = 0
            for x_p in range(max(0, pixel[0] - 1), min(width, pixel[0] + 2)):
                for y_p in range(max(0, pixel[1] - 1), min(height, pixel[1] + 2)):
                    if (x_p, y_p) not in pixels_to_fill:
                        count += 1
            opaque_neighbor_counts[pixel] = count

        count = max(opaque_neighbor_counts.values())
        if count == 0:
            return image_arr, set(), opaque_neighbor_counts, set()
        pixels_to_fill_next_iter = set()
        pixels_to_recount_next_iter = set()
        for pixel in pixels_to_fill:
            if opaque_neighbor_counts[pixel] == count:
                color = np.zeros_like(image_arr[pixel[0], pixel[1]], dtype=np.uint32)
                for x_p in range(max(0, pixel[0] - 1), min(width, pixel[0] + 2)):
                    for y_p in range(max(0, pixel[1] - 1), min(height, pixel[1] + 2)):
                        pixel_p = (x_p, y_p)
                        if pixel_p not in pixels_to_fill:
                            color += image_arr[x_p, y_p]
                        elif (
                            pixel_p in opaque_neighbor_counts
                            and opaque_neighbor_counts[pixel_p] != count
                        ):
                            pixels_to_recount_next_iter.add(pixel_p)
                image_arr[pixel[0], pixel[1]] = color // count
                opaque_neighbor_counts.pop(pixel)
            else:
                pixels_to_fill_next_iter.add(pixel)

        return (
            image_arr,
            pixels_to_fill_next_iter,
            opaque_neighbor_counts,
            pixels_to_recount_next_iter,
        )

    @classmethod
    @lru_cache(maxsize=1)
    def _get_runtime(
        cls,
    ) -> tuple[GPUDevice, GPUBindGroupLayout, tuple[GPUComputePipeline, ...]]:
        """Load the compute device and compile the three cached entry points.

        Returns:
            device, shared binding layout, and reset/count/fill pipelines
        Raises:
            MaskFillError: if the runtime or shader cannot load
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
            raise MaskFillError(f"Mask-filling runtime could not load: {exc}") from exc
        return device, binding_layout, pipelines

    @classmethod
    def _run_gpu(
        cls, img: Image.Image, mask: np.ndarray, masked_count: int
    ) -> Image.Image:
        """Fill a validated image through the compute pipeline.

        Arguments:
            img: grayscale or RGB image to fill
            mask: same-sized boolean array whose true pixels are masked
            masked_count: number of pixels initially requiring filling
        Returns:
            image with masked pixels filled using exact integer color averages
        Raises:
            MaskFillError: if the compute runtime cannot load or execution fails
        """
        mask_arr = np.asarray(mask, dtype=np.uint32)
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
        except MaskFillError:
            raise
        except Exception as exc:  # pragma: no cover - runtime specific
            raise MaskFillError(f"Mask-filling shader execution failed: {exc}") from exc
        if img.mode == "RGB":
            output = np.stack(
                (output & 255, (output >> 8) & 255, (output >> 16) & 255), axis=-1
            )
        return Image.fromarray(output.astype(np.uint8))

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
            MaskFillError: if filling fails to finish within the progress bound
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
            raise MaskFillError("Mask-filling shader exceeded its fill-round bound")
        finally:
            for buffer in buffers:
                buffer.destroy()
