#  Copyright 2020-2023 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Video within a pipeline."""
from __future__ import annotations

from logging import debug
from pathlib import Path
from typing import Any, Self, Sequence

import cv2

from pipescaler.common import PathLike, validate_output_file
from pipescaler.core.pipelines.pipe_object import PipeObject


class PipeVideo(PipeObject):
    """Video within a pipeline."""

    def __init__(
        self,
        *,
        video: cv2.VideoCapture | None = None,
        path: Path | None = None,
        name: str | None = None,
        parents: Self | Sequence[Self] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize.

        Arguments:
            video: Video; either video or path must be provided, and both may not be
              provided; if path is provided, video will be loaded from path on first
              access
            path: Path to video file; either video or path must be provided, and both
              may not be provided
            name: Name of video; if not provided will name of first parent video, and if
              that is not available will use filename of path excluding extension; one
              of these must be available
            parents: Parent video(s) from which this video is descended
            kwargs: Additional keyword arguments
        """
        if video is None and path is None:
            raise ValueError(
                f"{self.__class__.__name__} requires either a video or the path to a "
                f"video; neither has been provided."
            )
        if video and path:
            raise ValueError(
                f"{self.__class__.__name__} requires either a video or the path to a "
                f"video; both have been provided."
            )
        if video and name is None and parents is None:
            raise ValueError(
                f"{self.__class__.__name__} requires either a name or parents if video "
                f"is provided; neither has been provided."
            )
        super().__init__(path=path, name=name, parents=parents, **kwargs)

        self._video = video

    @property
    def video(self) -> cv2.VideoCapture:
        """Video; loaded from path if not already available."""
        if self._video is None:
            if self.path is None:
                raise ValueError(
                    f"{self.__class__.__name__} requires either a video or the path to "
                    f"a video; neither has been provided."
                )
            debug(f"{self}: Opening video '{self.location_name} from '{self.path}'")
            self._video = cv2.VideoCapture(str(self.path))
        return self._video

    @video.setter
    def video(self, video: cv2.VideoCapture) -> None:
        self._video = video

    def save(self, path: PathLike) -> None:
        """Save image to file and set path.

        Arguments:
            path: Path to which to save image
        """
        path = validate_output_file(path)
        # TODO: save
        self.path = path
        raise NotImplementedError()
