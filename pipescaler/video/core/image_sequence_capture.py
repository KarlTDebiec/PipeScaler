#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Read an ordered image sequence through the OpenCV capture interface."""

from __future__ import annotations

from pathlib import Path

import cv2
from cv2.typing import MatLike

from pipescaler.common.validation import val_input_path

__all__ = ["ImageSequenceCapture"]


class ImageSequenceCapture:
    """Sequential color-image capture with frame count and dimension metadata.

    All frames must have the same dimensions. No frame rate is inferred from file
    names. The capture supports `read`, `get`, `isOpened`, and `release`; unsupported
    metadata properties return zero, as with an OpenCV capture.
    """

    def __init__(self, frame_paths: tuple[Path, ...]):
        """Open the first frame and retain the ordered paths.

        Arguments:
            frame_paths: nonempty sequence of concrete image paths
        Raises:
            FileNotFoundError: if a frame path does not exist
            NotAFileError: if a frame path is not a file
            ValueError: if no frame paths are provided
            OSError: if the first frame cannot be decoded
        """
        if not frame_paths:
            raise ValueError("An image sequence must contain at least one frame.")
        self._frame_paths = tuple(val_input_path(frame_paths))
        self._first_frame: MatLike | None = cv2.imread(
            str(self._frame_paths[0]), cv2.IMREAD_COLOR
        )
        if self._first_frame is None:
            raise OSError(
                f"Cannot decode image-sequence frame '{self._frame_paths[0]}'."
            )
        self._height, self._width = self._first_frame.shape[:2]
        self._index = 0
        self._closed = False

    def get(self, prop_id: int) -> float:
        """Return supported OpenCV metadata, or zero for unknown properties.

        Arguments:
            prop_id: OpenCV capture property identifier
        Returns:
            frame count, dimensions, position, or zero
        """
        if self._closed:
            return 0.0
        return float(
            {
                cv2.CAP_PROP_FRAME_COUNT: len(self._frame_paths),
                cv2.CAP_PROP_FRAME_WIDTH: self._width,
                cv2.CAP_PROP_FRAME_HEIGHT: self._height,
                cv2.CAP_PROP_POS_FRAMES: self._index,
            }.get(prop_id, 0)
        )

    def isOpened(self) -> bool:  # noqa: N802 - OpenCV capture interface
        """Return whether the capture has been released.

        Returns:
            whether this capture remains open, including after EOF
        """
        return not self._closed

    def read(self) -> tuple[bool, MatLike | None]:
        """Decode the next frame without silently skipping failures.

        Returns:
            success and BGR image, or false and None at EOF or after release
        Raises:
            OSError: if a frame disappears, cannot be decoded, or changes dimensions
        """
        if self._closed or self._index == len(self._frame_paths):
            return False, None
        try:
            frame_path = val_input_path(self._frame_paths[self._index])
            if self._index == 0:
                frame = self._first_frame
                self._first_frame = None
            else:
                frame = cv2.imread(str(frame_path), cv2.IMREAD_COLOR)
            if frame is None:
                raise OSError(f"Cannot decode image-sequence frame '{frame_path}'.")
            if frame.shape[:2] != (self._height, self._width):
                raise OSError(
                    f"Image-sequence frame '{frame_path}' has different dimensions."
                )
        except BaseException:
            self.release()
            raise
        self._index += 1
        return True, frame

    def release(self):
        """Close the capture and discard the cached first frame, idempotently."""
        self._closed = True
        self._first_frame = None
