#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Image within a pipeline."""
from __future__ import annotations

from logging import debug
from pathlib import Path
from typing import Optional, Sequence, Union

from PIL import Image

from pipescaler.common import validate_input_file, validate_output_file
from pipescaler.core.image import remove_palette


class PipeImage:
    """Image within a pipeline."""

    def __init__(
        self,
        image: Optional[Image.Image] = None,
        path: Optional[Path] = None,
        *,
        name: Optional[str] = None,
        parents: Optional[Union[PipeImage, Sequence[PipeImage]]] = None,
        location: Optional[Path] = None,
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
        """
        if image is None and path is None:
            raise ValueError(
                "PipeImage requires either an image or the path to an image; "
                "neither has been provided."
            )
        if image is not None and path is not None:
            raise ValueError(
                "PipeImage requires either an image or the path to an image; "
                "both have been provided."
            )
        if image is not None and name is None and parents is None:
            raise ValueError(
                "PipeImage requires either a name or parents if image is provided; "
                "neither has been provided."
            )
        self._image = image
        self.path = path

        if parents is not None:
            if isinstance(parents, PipeImage):
                parents = [parents]
            if not isinstance(parents, list):
                parents = list(parents)
        self._parents = parents

        if name is not None:
            self._name = name
        elif self.parents is not None:
            self._name = self.parents[0].name
        elif self.path is not None:
            self._name = self.path.stem
        else:
            raise ValueError(
                "PipeImage requires either a name, the path to an image whose filename "
                "will be used as the name, or a parent image whose name will be used."
            )

        if location is not None:
            self._location: Optional[Path] = location
        elif self.parents is not None:
            self._location = self.parents[0].location
        else:
            self._location = None

    def __str__(self) -> str:
        """String representation."""
        return (
            f"<PipeImage '{self.name}' "
            f"of mode={self.image.mode} "
            f"and size={self.image.size} "
            f"and parents={self.count_parents()}>"
        )

    def count_parents(self) -> int:
        """Count number of parents of this image."""
        if self.parents is not None:
            return len(self.parents) + sum(p.count_parents() for p in self.parents)
        return 0

    def save(self, path: Union[Path, str]) -> None:
        """Save image to file and set path.

        Arguments:
            path: Path to which to save image
        """
        path = validate_output_file(path)
        self.image.save(path)
        self.path = path

    @property
    def image(self) -> Image.Image:
        """Actual image; loaded from path is not already available."""
        if self._image is None:
            if self.path is None:
                raise ValueError(
                    "PipeImage requires either an image or the path to an image; "
                    "neither has been provided."
                )
            debug(f"<PipeImage>: Opening image {self.name} from '{self.path}'")
            image = Image.open(self.path)
            if image.mode == "P":
                image = remove_palette(image)
            self._image = image
        return self._image

    @image.setter
    def image(self, value: Image.Image) -> None:
        self._image = value

    @property
    def parents(self) -> Optional[list[PipeImage]]:
        """Parent images of this image."""
        return self._parents

    @property
    def path(self) -> Optional[Path]:
        """Path to this image, if applicable."""
        return self._path

    @path.setter
    def path(self, value: Optional[Union[Path, str]]) -> None:
        if value is not None:
            value = validate_input_file(value)
        self._path = value

    @property
    def name(self) -> str:
        """Name of this image."""
        return self._name

    @property
    def location_name(self) -> str:
        """Location relative to root directory and name."""
        if self.location is not None:
            return str(self.location / self.name)
        return self.name

    @property
    def location(self) -> Optional[Path]:
        """Location relative to root directory."""
        return self._location
