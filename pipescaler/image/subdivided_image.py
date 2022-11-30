#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Image divided into subdivisions."""
import numpy as np
from PIL import Image
from scipy.special import erf

from pipescaler.common import validate_int


class SubdividedImage:
    """Image divided into subdivisions."""

    def __init__(self, image: Image.Image, size: int, overlap: int) -> None:
        """Initialize.

        Arguments:
            image: Image to subdivide
            size: Size of subdivisions
            overlap: Overlap between subdivisions
        """
        self.image = image
        self.size = validate_int(size, 4)
        self.overlap = validate_int(overlap, 2)
        self.boxes = self.get_boxes(image.width, image.height, self.size, self.overlap)

        self._subs = self.get_subs(image, self.boxes)

    @property
    def subs(self) -> list[Image.Image]:
        """Subdivisions of image.

        When changed, the new size of the subdivisions is compared to the current size.
        If it has changed, size, overlap, and boxes are scaled accordingly, and the
        image is recomposed from the new subdivisions. The new subdivisions are then
        re-extracted from the recomposed image. A consequence of this is that setting
        subs to a particular value will not necessarily result in subs being set to
        that value.
        """
        return self._subs

    @subs.setter
    def subs(self, value: list[Image.Image]) -> None:
        if len(value) != len(self._subs):
            raise ValueError(
                f"Expected {len(self._subs)} subdivisions, received {len(value)}"
            )
        scale = int(value[0].width / self._subs[0].width)
        if scale != 1:
            self.size *= scale
            self.overlap *= scale
            self.boxes *= scale

        self.image = self.get_recomposed_image(
            value, self.boxes, self.size, self.overlap
        )
        self._subs = self.get_subs(self.image, self.boxes)

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
        width = boxes[:, 2].max()
        height = boxes[:, 3].max()
        n_dim = len(subs[0].getbands())

        # Prepare arrays to hold image data and total weights
        if n_dim == 1:
            recomposed_array = np.zeros((height, width), float)
        else:
            recomposed_array = np.zeros((height, width, n_dim), float)
        recomposed_weights = np.zeros((height, width), float)

        # Sum image data and weights
        weights = cls.get_sub_weights(boxes, size, overlap)
        for sub, box, weight in zip(subs, boxes, weights):
            sub_array = np.array(sub).astype(float)
            if n_dim == 1:
                sub_array *= weight
            else:
                sub_array *= np.stack([weight] * n_dim, axis=2)
            recomposed_array[box[1] : box[3], box[0] : box[2]] += sub_array
            recomposed_weights[box[1] : box[3], box[0] : box[2]] += weight

        # Normalize image data and convert to image
        if n_dim == 1:
            recomposed_array /= recomposed_weights
        else:
            recomposed_array /= np.stack([recomposed_weights] * n_dim, axis=2)
        recomposed_array = np.clip(np.round(recomposed_array), 0, 255).astype(np.uint8)

        return Image.fromarray(recomposed_array)

    @classmethod
    def get_sub_weights(
        cls, boxes: np.ndarray, size: int, overlap: int
    ) -> list[np.ndarray]:
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
    def get_subs(image: Image.Image, boxes: np.ndarray) -> list[Image.Image]:
        """Get subdivisions of image.

        Arguments:
            image: Image to be subdivided
            boxes: Boxes for subdivisions in form of [[left, upper, right, lower], ...]

        Returns:
            Subdivisions of image
        """
        return [image.crop(box) for box in boxes]

    @staticmethod
    def get_sub_count(full_size: int, size: int, overlap: int) -> int:
        """Get number of subdivisions in one dimension.

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
        adjusted_x = ((4 * x) / (overlap - 1)) - 2
        taper = (erf(adjusted_x) + 1) / 2

        left = np.tile(taper, (size, 1))
        top = np.tile(np.reshape(taper, (overlap, 1)), (1, size))
        right = np.tile(taper[::-1], (size, 1))
        bottom = np.tile(np.reshape(taper, (overlap, 1))[::-1], (1, size))

        return left, top, right, bottom
