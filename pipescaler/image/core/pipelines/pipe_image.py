#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Image within a pipeline."""
from __future__ import annotations

from logging import debug
from pathlib import Path
from typing import Any, Self, Sequence

from PIL import Image

from pipescaler.common.typing import PathLike
from pipescaler.common.validation import validate_output_file
from pipescaler.core.pipelines import PipeObject
from pipescaler.image.core.functions import remove_palette


class PipeImage(PipeObject):
    """Image within a pipeline."""

    def __init__(
        self,
        *,
        image: Image.Image | None = None,
        path: Path | None = None,
        name: str | None = None,
        parents: Self | Sequence[Self] | None = None,
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
            kwargs: Additional keyword arguments
        """
        if image is None and path is None:
            raise ValueError(
                f"{self.__class__.__name__} requires either an image or the path to an "
                f"image; neither has been provided."
            )
        if image and path:
            raise ValueError(
                f"{self.__class__.__name__} requires either an image or the path to an "
                f"image; both have been provided."
            )
        if image and name is None and parents is None:
            raise ValueError(
                f"{self.__class__.__name__} requires either a name or parents if image "
                f"is provided; neither has been provided."
            )
        super().__init__(path=path, name=name, parents=parents, **kwargs)

        self._image = image

    @property
    def image(self) -> Image.Image:
        """Image; loaded from path if not already available."""
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

    def save(self, path: PathLike) -> None:
        """Save image to file and set path.

        Arguments:
            path: Path to which to save image
        """
        path = validate_output_file(path)
        self.image.save(path)
        self.path = path
