#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Image divided into subdivisions."""

from __future__ import annotations

from collections.abc import Iterable, Iterator

import numpy as np
from PIL import Image
from scipy.special import erf

from pipescaler.common.validation import val_int

from .core.validation import validate_image_scale

__all__ = ["SubdividedImage"]


class SubdividedImage:
    """Image divided into subdivisions."""

    def __init__(self, image: Image.Image, size: int, overlap: int):
        """Initialize.

        Arguments:
            image: Image to subdivide
            size: Size of subdivisions
            overlap: Non-negative overlap smaller than size
        Raises:
            ValueError: if overlap is negative or not smaller than size
        """
        self.image = image
        self.size = val_int(size, min_value=4)
        self.overlap = val_int(overlap, min_value=0)
        if self.overlap >= self.size:
            raise ValueError("overlap must be less than size")
        self.boxes = self.get_boxes(image.width, image.height, self.size, self.overlap)

        self._subs = self.get_subs(image, self.boxes)

    def __repr__(self) -> str:
        """Representation.

        Returns:
            string representation of this object
        """
        return (
            f"{self.__class__.__name__}("
            f"image={self.image!r}, "
            f"size={self.size!r}, "
            f"overlap={self.overlap!r})"
        )

    @property
    def subs(self) -> list[Image.Image]:
        """Subdivisions of image.

        When changed, subdivision dimensions must use the same positive integer scale.
        Size, overlap, and boxes are scaled accordingly, and the image is recomposed
        from the new subdivisions. The new subdivisions are then re-extracted from
        the recomposed image. A consequence of this is that setting subs to a
        particular value will not necessarily result in subs being set to that value.
        """
        return self._subs

    @subs.setter
    def subs(self, value: list[Image.Image]):
        """Set subdivisions and update internal geometry as needed.

        Arguments:
            value: new value to assign
        Raises:
            ValueError: if input values or configuration are invalid
        """
        if len(value) != len(self._subs):
            raise ValueError(
                f"Expected {len(self._subs)} subdivisions, received {len(value)}"
            )
        scales = set()
        for new_sub, old_sub in zip(value, self._subs):
            scales.add(validate_image_scale(old_sub, new_sub))
        if len(scales) != 1:
            raise ValueError(
                "All subdivisions must use the same positive integer scale"
            )

        scale = next(iter(scales))
        boxes = self.boxes * scale
        size = self.size * scale
        overlap = self.overlap * scale
        image = self.get_recomposed_image(value, boxes, size, overlap)
        subs = self.get_subs(image, boxes)
        self.image = image
        self.boxes = boxes
        self.size = size
        self.overlap = overlap
        self._subs = subs

    @classmethod
    def get_boxes(cls, width: int, height: int, size: int, overlap: int) -> np.ndarray:
        """Get subdivisions of image in format of (left, upper, right, lower).

        Arguments:
            width: Width of image
            height: Height of image
            size: Size of subdivisions
            overlap: Overlap of subdivisions
        Returns:
            Boxes for subdivisions in format of (left, upper, right, lower)
        """
        x_sub_count = cls.get_sub_count(width, size, overlap)
        x_sub_edges = cls.get_sub_edges(width, size, x_sub_count)
        y_sub_count = cls.get_sub_count(height, size, overlap)
        y_sub_edges = cls.get_sub_edges(height, size, y_sub_count)

        boxes = []
        for x_sub_edge in x_sub_edges:
            for y_sub_edge in y_sub_edges:
                box = (x_sub_edge[0], y_sub_edge[0], x_sub_edge[1], y_sub_edge[1])
                boxes.append(box)

        return np.array(boxes)

    @classmethod
    def get_recomposed_image(
        cls, subs: list[Image.Image], boxes: np.ndarray, size: int, overlap: int
    ) -> Image.Image:
        """Get recomposed image from subdivisions.

        Arguments:
            subs: Subdivisions of image
            boxes: Boxes for subdivisions in format of (left, upper, right, lower)
            size: Size of subdivisions
            overlap: Overlap of subdivisions
        Returns:
            Recomposed image
        """
        recomposed_arr = cls.recompose_float(
            (np.asarray(sub, dtype=np.float32) for sub in subs), boxes, size, overlap
        )
        recomposed_arr = np.clip(np.round(recomposed_arr), 0, 255).astype(np.uint8)

        return Image.fromarray(recomposed_arr)

    @classmethod
    def get_sub_weights(
        cls, boxes: np.ndarray, size: int, overlap: int
    ) -> Iterator[np.ndarray]:
        """Get weights for each subdivision to be used when recomposing full image.

        Arguments:
            boxes: Boxes for subdivisions in form of [[left, upper, right, lower], ...]
            size: Size of subdivisions
            overlap: Overlap of subdivisions
        Yields:
            weights for one subdivision at a time, without retaining all weights
        """
        left, top, right, bottom = cls.get_sub_edge_tapers(size, overlap)

        for box in boxes:
            height = box[3] - box[1]
            width = box[2] - box[0]
            weight = np.ones((height, width), np.float32)
            if overlap and box[0] != 0:
                extent = min(overlap, width)
                weight[:, :extent] = np.minimum(
                    weight[:, :extent], left[:height, :extent]
                )
            if overlap and box[1] != 0:
                extent = min(overlap, height)
                weight[:extent, :] = np.minimum(
                    weight[:extent, :], top[:extent, :width]
                )
            if overlap and box[2] != boxes[:, 2].max():
                extent = min(overlap, width)
                weight[:, -extent:] = np.minimum(
                    weight[:, -extent:], right[:height, -extent:]
                )
            if overlap and box[3] != boxes[:, 3].max():
                extent = min(overlap, height)
                weight[-extent:, :] = np.minimum(
                    weight[-extent:, :], bottom[-extent:, :width]
                )
            yield weight

    @classmethod
    def recompose_float(
        cls, subs: Iterable[np.ndarray], boxes: np.ndarray, size: int, overlap: int
    ) -> np.ndarray:
        """Blend a stream of floating-point tiles without image quantization.

        Only the output, normalization weights, and current tile are retained.
        Boxes, size, and overlap use output pixels, including any native scale.

        Arguments:
            subs: tiles in box order; arrays may be grayscale or HWC
            boxes: nonempty integer crop boxes covering the output
            size: maximum tile extent in output pixels
            overlap: overlap in output pixels
        Returns:
            normalized float32 array retaining fractional channel values
        Raises:
            ValueError: if tile count, shape, values, or coverage is invalid
            TypeError: if a tile is not floating-point
        """
        if boxes.ndim != 2 or boxes.shape[1] != 4 or len(boxes) == 0:
            raise ValueError("Expected nonempty tile boxes with shape (count, 4)")
        width, height = boxes[:, 2].max(), boxes[:, 3].max()
        if np.any(boxes[:, :2] < 0) or np.any(boxes[:, 2:] <= boxes[:, :2]):
            raise ValueError("Tile boxes must have positive dimensions and coordinates")
        output = None
        total_weights = np.zeros((height, width), np.float32)
        for sub, box, weight in zip(
            subs, boxes, cls.get_sub_weights(boxes, size, overlap), strict=True
        ):
            if not np.issubdtype(sub.dtype, np.floating):
                raise TypeError("Reconstruction requires floating-point tiles")
            if sub.ndim not in {2, 3} or sub.shape[:2] != weight.shape:
                raise ValueError("Tile dimensions do not match their output box")
            if not np.isfinite(sub).all():
                raise ValueError("Tile values must be finite")
            if output is None:
                output = np.zeros((height, width, *sub.shape[2:]), np.float32)
            elif sub.shape[2:] != output.shape[2:]:
                raise ValueError("Tiles must have the same channel dimensions")
            region = np.s_[box[1] : box[3], box[0] : box[2]]
            output[region] += sub * (weight if sub.ndim == 2 else weight[:, :, None])
            total_weights[region] += weight
        if output is None or np.any(total_weights <= 0):
            raise ValueError("Tile boxes must cover the output without holes")
        output /= total_weights if output.ndim == 2 else total_weights[:, :, None]
        return output

    @staticmethod
    def get_sub_count(full_size: int, size: int, overlap: int) -> int:
        """Get number of subdivisions in one dimension.

        Arguments:
            full_size: Full size of image in this dimension
            size: Size of each subdivision
            overlap: Non-negative overlap smaller than subdivision size
        Returns:
            number of subdivisions
        """
        count = max(
            1, 2 + int(np.ceil((full_size - (2 * size) + overlap) / (size - overlap)))
        )

        return count

    @staticmethod
    def get_sub_edge_tapers(
        size: int, overlap: int
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Get weights for tapering edges of subdivisions during recomposition.

        Weights are generated using the error function, whose x range  from (-2, 2)
        is shifted to (0, overlap - 1) and whose y range from (-1, 1) is shifted to
        (0, 1).

        For example, for an overlap of 8 pixels, the weights yielded are
        (0.002, 0.022, 0.113, 0.343, 0.657, 0.887, 0.978, 0.998), which for a channel
        with an original value of 255 yield (1, 6, 29, 87, 168, 226, 249, 254).

        These weights are then rotated and tiled, yielding four arrays that can be
        used to taper the left, top, right, and bottom edges of subdivisions during
        recomposition.

        Arguments:
            size: Size of subdivisions
            overlap: Overlap between subdivisions
        Returns:
            Weights for tapering along left, top, right, and bottom edges
        """
        x = np.arange(overlap)
        if overlap == 1:
            taper = np.array([0.5])
        else:
            adjusted_x = ((4 * x) / (overlap - 1)) - 2
            taper = (erf(adjusted_x) + 1) / 2

        left = np.tile(taper, (size, 1))
        top = np.tile(np.reshape(taper, (overlap, 1)), (1, size))
        right = np.tile(taper[::-1], (size, 1))
        bottom = np.tile(np.reshape(taper, (overlap, 1))[::-1], (1, size))

        return left, top, right, bottom

    @staticmethod
    def get_sub_edges(full_size: int, sub_size: int, count: int) -> np.ndarray:
        """Get edges of subdivisions in one dimension.

        Arguments:
            full_size: Full size of image in this dimension
            sub_size: Size of each subdivision
            count: number of subdivisions
        Returns:
            Edges of subdivisions
        """
        if count == 1:
            return np.array([[0, full_size]], dtype=int)
        overlap = int(((count * sub_size) - full_size) / (count - 1))
        centers = np.round(
            np.linspace(
                sub_size - overlap + np.floor(sub_size / 2),
                full_size - sub_size + overlap - np.ceil(sub_size / 2),
                count - 2,
            )
        ).astype(int)
        left_edges = centers - int(np.floor(sub_size / 2))
        right_edges = centers + int(np.ceil(sub_size / 2))
        edges = np.array(
            [(0, sub_size)]
            + list(zip(left_edges, right_edges))
            + [(full_size - sub_size, full_size)]
        )

        return edges

    @staticmethod
    def get_subs(image: Image.Image, boxes: np.ndarray) -> list[Image.Image]:
        """Get subdivisions of image.

        Arguments:
            image: Image to be subdivided
            boxes: Boxes for subdivisions in form of [[left, upper, right, lower], ...]
        Returns:
            Subdivisions of image
        """
        return [image.crop(tuple(box)) for box in boxes]
