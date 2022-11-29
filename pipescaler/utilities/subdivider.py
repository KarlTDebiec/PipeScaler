#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
from typing import Optional

import numpy as np
from PIL import Image
from scipy.special import erf

from pipescaler.common import validate_int
from pipescaler.core import Utility

# [x] Subdivide image into subdivisions of provided size and overlap
# [x] Loop over images, perform operations on each, and store results
# [x] Calculate weights for each subdivision based on overlap and location
# [ ] Recompose subdivisions into a single image
# [ ] Recompose scaled subdivisions into a single image

np.set_printoptions(threshold=np.inf)


class SubdividedImage:
    def __init__(self, image: Image.Image, boxes: np.array) -> None:
        self._image = image
        self.boxes = boxes
        self.scale = 1
        self._subs = [image.crop(box) for box in boxes]

    @property
    def image(self) -> Optional[Image.Image]:
        """Un-subdivided image"""
        return self._image

    @image.setter
    def image(self, value: Optional[Image.Image]) -> None:
        self._image = value

    @property
    def subs(self) -> list[Image.Image]:
        """Subdivisions of image"""
        return self._subs

    @subs.setter
    def subs(self, value: list[Image.Image]) -> None:
        if len(value) != len(self._subs):
            raise ValueError(
                f"Expected {len(self._subs)} subdivisions, received {len(value)}"
            )
        original_size = self._subs[0].width
        new_size = value[0].width
        self.image = None
        self.scale = int(new_size / original_size)
        self.boxes *= self.scale
        self._subs = value


class Subdivider(Utility):
    def __init__(self, size: int = 128, overlap: int = 8) -> None:
        self.size = validate_int(size, 4)
        self.overlap = validate_int(overlap, 2)

    def recompose(self, subdivided_image: SubdividedImage) -> Image.Image:
        subs = subdivided_image.subs
        boxes = subdivided_image.boxes
        scale = subdivided_image.scale

        width = boxes[:, 3].max()
        height = boxes[:, 2].max()
        n_dim = {"L": 1, "RGB": 3}[subs[0].mode]

        recomposed_array = np.zeros((width, height, n_dim), float)
        recomposed_weights = np.zeros((width, height), float)

        weights = self.get_sub_weights(boxes, self.size * scale, self.overlap * scale)
        for sub, box, weight in zip(subs, boxes, weights):
            sub_array = np.array(sub).astype(float)
            weighted_sub_array = sub_array * np.stack([weight] * n_dim, axis=2)
            recomposed_array[box[1] : box[3], box[0] : box[2]] += weighted_sub_array
            recomposed_weights[box[1] : box[3], box[0] : box[2]] += weight
            print("a")

        recomposed_array = recomposed_array / np.stack(
            [recomposed_weights] * n_dim, axis=2
        )
        recomposed_array = np.clip(np.round(recomposed_array), 0, 255).astype(np.uint8)
        recomposed_image = Image.fromarray(recomposed_array)

        return recomposed_image

    def subdivide(self, image: Image.Image) -> SubdividedImage:
        """Subdivide an image into subdivisions

        Arguments:
            image: Image to subdivide
        Returns:
            Subdivided image
        """
        boxes = self.get_boxes(image.width, image.height, self.size, self.overlap)

        return SubdividedImage(image, boxes)

    @classmethod
    def get_boxes(cls, width: int, height: int, size: int, overlap: int) -> np.array:
        """Get subdivisions of image in format of (left, upper, right, lower)

        Arguments
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
        boxes = np.array(boxes)

        return boxes

    @classmethod
    def get_sub_weights(cls, boxes: np.array, size: int, overlap: int) -> np.array:
        """Get weights for each subdivision to be used when recomposing full image.

        Arguments:
            boxes: Boxes for subdivisions in form of [[left, upper, right, lower], ...]
            size: Size of subdivisions
            overlap: Overlap of subdivisions
        Returns:
            Weights for each subdivision to be used when recomposing full image
        """
        left, top, right, bottom = cls.get_sub_edge_tapers(size, overlap)

        weights = []
        for box in boxes:
            weight = np.ones((box[3] - box[1], box[2] - box[0]), float)
            if box[0] != 0:
                weight[:, :overlap] = np.minimum(weight[:, :overlap], left)
            if box[1] != 0:
                weight[:overlap, :] = np.minimum(weight[:overlap, :], top)
            if box[2] != boxes[:, 2].max():
                weight[:, -overlap:] = np.minimum(weight[:, -overlap:], right)
            if box[3] != boxes[:, 3].max():
                weight[-overlap:, :] = np.minimum(weight[-overlap:, :], bottom)
            weights.append(weight)

        return weights

    @staticmethod
    def get_sub_count(full_size: int, size: int, overlap: int) -> int:
        """Get number of subdivisions in one dimension

        Arguments:
            full_size: Full size of image in this dimension
            size: Size of each subdivision
            overlap: Overlap between subdivisions
        Returns:
            Number of subdivisions
        """
        count = 2 + int(np.ceil((full_size - (2 * size) + overlap) / (size - overlap)))

        return count

    @staticmethod
    def get_sub_edges(full_size: int, sub_size: int, count: int) -> np.ndarray:
        """Get edges of subdivisions in one dimension.

        Arguments:
            full_size: Full size of image in this dimension
            sub_size: Size of each subdivision
            count: Number of subdivisions
        Returns:
            Edges of subdivisions
        """
        if count == 1:
            return np.array([[0, full_size]], dtype=np.int)
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
    def get_sub_edge_tapers(
        size: int, overlap: int
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Get weights for tapering edges of subdivisions during recompoision.

        Weights are generated using the error function, whose x range  from (-2, 2)
        is shifted to (0, overlap - 1) and whose y range from (-1, 1) is shifted to
        (0, 1).

        For example, for an overlap of 8 pixels, the weights yielded are
        (0.002, 0.022, 0.113, 0.343, 0.657, 0.887, 0.978, 0.998), which for a channel
        with an original value of 255 yield (1, 6, 29, 87, 168, 226, 249, 254).

        Arguments:
            size: Size of subdivisions
            overlap: Overlap between subdivisions
        Returns:
            Weights for tapering along left, top, right, and bottom edges
        """
        x = np.arange(overlap)
        adjusted_x = ((4 * x) / (overlap - 1)) - 2
        taper = (erf(adjusted_x) + 1) / 2

        left = np.tile(taper, (size, 1))
        top = np.tile(np.reshape(taper, (overlap, 1)), (1, size))
        right = np.tile(taper[::-1], (size, 1))
        bottom = np.tile(np.reshape(taper, (overlap, 1))[::-1], (1, size))

        return left, top, right, bottom
