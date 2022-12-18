#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Image within a pipeline."""
from __future__ import annotations

from logging import debug
from pathlib import Path
from typing import Any, Optional, Sequence, Union

from PIL import Image

from pipescaler.common import PathLike, validate_output_file
from pipescaler.core.image import remove_palette
from pipescaler.core.pipelines.pipe_object import PipeObject


class PipeImage(PipeObject):
    """Image within a pipeline."""

    def __init__(
        self,
        *,
        image: Optional[Image.Image] = None,
        path: Optional[Path] = None,
        name: Optional[str] = None,
        parents: Optional[Union[PipeImage, Sequence[PipeImage]]] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize.

        Arguments:
            image: Image; either image or path must be provided, and both may not be
              provided; if path is provided, image will be loaded from path on first
              access
            path: Path to image file; either image or path must be provided, and both
              may not be provided
            name: Name of image; if not provided will name of first parent image, and if
              that is not available will use filename of path excluding extension; one
              of these must be available
            parents: Parent image(s) from which this image is descended
            location: Path relative to parent directory
            kwargs: Additional keyword arguments
        """
        if image is None and path is None:
            raise ValueError(
                f"{self.__class__.__name__} requires either an image or the path to an "
                f"image; neither has been provided."
            )
        if image is not None and path is not None:
            raise ValueError(
                f"{self.__class__.__name__} requires either an image or the path to an "
                f"image; both have been provided."
            )
        if image is not None and name is None and parents is None:
            raise ValueError(
                f"{self.__class__.__name__} requires either a name or parents if image "
                f"is provided; neither has been provided."
            )
        super().__init__(path=path, name=name, parents=parents, **kwargs)

        self._image = image

    def save(self, path: PathLike) -> None:
        """Save image to file and set path.

        Arguments:
            path: Path to which to save image
        """
        path = validate_output_file(path)
        self.image.save(path)
        self.path = path

    @property
    def image(self) -> Image.Image:
        """Image; loaded from path is not already available."""
        if self._image is None:
            if self.path is None:
                raise ValueError(
                    f"{self.__class__.__name__} requires either an image or the path "
                    f"to an image; neither has been provided."
                )
            debug(f"{self}: Opening image '{self.location_name}' from '{self.path}'")
            image = Image.open(self.path)
            if image.mode == "P":
                image = remove_palette(image)
            self._image = image
        return self._image

    @image.setter
    def image(self, value: Image.Image) -> None:
        self._image = value
