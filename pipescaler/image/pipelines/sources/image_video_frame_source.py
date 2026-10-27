#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Yields images from a video file."""

from __future__ import annotations

import math
from pathlib import Path
from types import TracebackType
from typing import Any, Self

import cv2
from PIL import Image

from pipescaler.common.validation import val_input_path
from pipescaler.image.core.pipelines import ImageSource, PipeImage

__all__ = ["ImageVideoFrameSource"]


class ImageVideoFrameSource(ImageSource):
    """Yields sequential frames and owns the video capture.

    Exhaustion and decoding errors close the capture. Call `close()` or use a
    `with` block when iteration may stop early. A positive integral frame count
    detects premature decoding failure, but never limits sequential reading.
    With no usable count, OpenCV cannot distinguish EOF from decoding failure.
    """

    def __init__(
        self,
        input_path: Path | str,
        location_path: Path | None = None,
        **kwargs: Any,
    ):
        """Initialize and open the video.

        Arguments:
            input_path: video file from which to yield images
            location_path: path relative to parent directory
            **kwargs: additional keyword arguments
        Raises:
            OSError: if the video cannot be opened
        """
        super().__init__(**kwargs)

        self.input_path = val_input_path(input_path)
        """Path to video file."""
        self.location_path = location_path
        """Path relative to parent directory."""
        self.cap = cv2.VideoCapture(str(self.input_path))
        """Capture owned by this source; released by `close()`."""
        self._closed = False
        self.index = 0
        """Number of successfully yielded frames."""
        try:
            if not self.cap.isOpened():
                raise OSError(f"Cannot open video '{self.input_path}'.")
            count = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
            if math.isfinite(count) and count > 0 and count.is_integer():
                self.length = int(count)
            else:
                self.length = None
            """Reported frame count, or None when unavailable or invalid."""
        except BaseException:
            self.close()
            raise

    def __enter__(self) -> Self:
        """Return this source for deterministic capture cleanup.

        Returns:
            this open source
        Raises:
            ValueError: if this source is already closed
        """
        if self._closed:
            raise ValueError("Cannot enter a closed video frame source.")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ):
        """Close the capture without suppressing exceptions.

        Arguments:
            exc_type: active exception type, if any
            exc_value: active exception, if any
            traceback: active traceback, if any
        """
        self.close()

    def __next__(self) -> PipeImage:
        """Read the next frame without seeking.

        Returns:
            next object yielded by this source
        Raises:
            StopIteration: when closed or decoding reaches EOF
            OSError: if decoding fails before a known count or returns no frame
        """
        if self._closed:
            raise StopIteration
        try:
            success, frame = self.cap.read()
            if not success:
                if self.length is not None and self.index < self.length:
                    raise OSError(
                        f"Cannot decode frame {self.index + 1} of "
                        f"{self.length} in video '{self.input_path}'."
                    )
                raise StopIteration
            if frame is None:
                raise OSError(
                    f"Decoder returned no frame {self.index + 1} "
                    f"in video '{self.input_path}'."
                )
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            location_path = Path(
                f"{self.input_path.stem}_{self.input_path.suffix.lstrip('.')}"
            )
            if self.location_path:
                location_path = self.location_path / location_path
            obj = PipeImage(
                image=img,
                name=f"{self.index + 1:06d}",
                location_path=location_path,
            )
        except BaseException:
            self.close()
            raise
        self.index += 1
        return obj

    def __repr__(self) -> str:
        """Representation.

        Returns:
            string representation of this object
        """
        input_path = f"Path({str(self.input_path)!r})"
        location_path = repr(self.location_path)
        if self.location_path is not None:
            location_path = f"Path({str(self.location_path)!r})"
        return (
            f"{self.__class__.__name__}(input_path={input_path}, "
            f"location_path={location_path})"
        )

    def close(self):
        """Release the owned capture once and permanently stop iteration."""
        if not self._closed:
            self._closed = True
            self.cap.release()
