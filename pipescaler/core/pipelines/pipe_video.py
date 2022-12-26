#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Video within a pipeline."""
from __future__ import annotations

from logging import debug
from pathlib import Path
from typing import Any, Optional, Sequence, Union

import cv2

from pipescaler.core.pipelines.pipe_object import PipeObject


class PipeVideo(PipeObject):
    """Video within a pipeline."""

    def __init__(
        self,
        *,
        video: Optional[cv2.VideoCapture] = None,
        path: Optional[Path] = None,
        name: Optional[str] = None,
        parents: Optional[Union[PipeVideo, Sequence[PipeVideo]]] = None,
        **kwargs: Any,
    ) -> None:
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
