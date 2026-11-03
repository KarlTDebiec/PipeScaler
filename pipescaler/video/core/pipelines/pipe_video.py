#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Video within a pipeline."""

from __future__ import annotations

from collections.abc import Sequence
from logging import getLogger
from pathlib import Path
from typing import Any, Self

import cv2

from pipescaler.core.pipelines.pipe_object import PipeObject
from pipescaler.video.core.image_sequence_capture import ImageSequenceCapture
from pipescaler.video.core.video_input import VideoInput

__all__ = ["PipeVideo"]

logger = getLogger(__name__)


class PipeVideo(PipeObject):
    """Video file, numbered image sequence, or capture within a pipeline.

    Sequence templates accept one `%d` or `%0Nd` placeholder in a filename or
    directory component. `input_path` retains the template while `path` is None,
    since a sequence is not a concrete video file.
    """

    def __init__(
        self,
        *,
        video: cv2.VideoCapture | ImageSequenceCapture | None = None,
        path: Path | str | None = None,
        name: str | None = None,
        parents: Self | Sequence[Self] | None = None,
        **kwargs: Any,
    ):
        """Initialize.

        Arguments:
            video: Video; either video or path must be provided, and both may not be
              provided; if path is provided, video will be loaded from path on first
              access
            path: video file or numbered image-sequence template; mutually exclusive
              with video
            name: Name of video; if not provided will name of first parent video, and if
              that is not available will use the file stem or the sequence directory
              name with its template identifier
            parents: Parent video(s) from which this video is descended
            **kwargs: Additional keyword arguments
        Raises:
            DirectoryNotFoundError: if the sequence root directory does not exist
            FileNotFoundError: if the input file or matching frames do not exist
            NotADirectoryError: if the sequence root is not a directory
            TypeError: if the input cannot be cast to a path
            ValueError: if input values or configuration are invalid
        """
        if video is None and path is None:
            raise ValueError(
                f"{self.__class__.__name__} requires either a video or the path to a "
                f"video; neither has been provided."
            )
        if video is not None and path is not None:
            raise ValueError(
                f"{self.__class__.__name__} requires either a video or the path to a "
                f"video; both have been provided."
            )
        if video is not None and name is None and parents is None:
            raise ValueError(
                f"{self.__class__.__name__} requires either a name or parents if video "
                f"is provided; neither has been provided."
            )
        video_input = VideoInput(path) if path is not None else None
        self._sequence_input: VideoInput | None = None
        if video_input is not None and video_input.frame_paths is not None:
            self._sequence_input = video_input
            path = None
            if name is None and not parents:
                name = video_input.name
        super().__init__(path=path, name=name, parents=parents, **kwargs)

        self._video = video

    def __repr__(self) -> str:
        """Return a reconstructible file or sequence specification.

        Returns:
            constructor expression preserving the input template and lineage
        """
        input_path = "None"
        if self.input_path is not None:
            input_path = f"Path({str(self.input_path)!r})"
        location_path = "None"
        if self.location is not None:
            location_path = f"Path({str(self.location)!r})"
        return (
            f"{self.__class__.__name__}("
            f"path={input_path}, "
            f"name={self.name!r}, "
            f"parents={self.parents!r}, "
            f"location_path={location_path})"
        )

    @property
    def input_path(self) -> Path | None:
        """Concrete input file path or numbered image-sequence template."""
        if self.path is not None:
            return self.path
        if self._sequence_input is not None:
            return self._sequence_input.input_path
        return None

    @property
    def video(self) -> cv2.VideoCapture | ImageSequenceCapture:
        """Video; loaded from path if not already available.

        Raises:
            ValueError: if no capture or input path is available
            OSError: if the input cannot be opened
        """
        if self._video is None:
            if self.path is not None:
                video_input = VideoInput(self.path)
            elif self._sequence_input is not None:
                video_input = self._sequence_input
            else:
                raise ValueError(
                    f"{self.__class__.__name__} requires either a video or the path to "
                    f"a video; neither has been provided."
                )
            logger.debug(
                f"{self}: Opening video '{self.location_name}' from '{self.input_path}'"
            )
            self._video = video_input.open_capture()
        return self._video

    @video.setter
    def video(self, video: cv2.VideoCapture | ImageSequenceCapture):
        """Set video capture instance.

        Arguments:
            video: video object to assign
        """
        self._video = video

    def save(self, path: Path | str):
        """Reject unsupported video encoding without changing state or files.

        Arguments:
            path: requested output path
        Raises:
            NotImplementedError: always, because video encoding is unsupported
        """
        raise NotImplementedError("PipeVideo.save does not support video encoding")
