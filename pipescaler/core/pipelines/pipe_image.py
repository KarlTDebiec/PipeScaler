#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Image within a pipeline."""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Sequence, Union

from PIL import Image

from pipescaler.common import validate_input_file
from pipescaler.core.image import remove_palette


class PipeImage:
    """Image within a pipeline."""

    def __init__(
        self,
        image: Optional[Image.Image] = None,
        path: Optional[Union[Path, str]] = None,
        parents: Optional[Union[PipeImage, Sequence[PipeImage]]] = None,
        name: Optional[str] = None,
    ) -> None:
        """Validate and initialize.

        Arguments:
            image: Image; if not provided, path must be provided, and image will be
              loaded from path on first access
            path: Path to image file; if not provided, image must be provided; while
              both image and path may not be provided at creation, path may be set later
              if image is to be saved
            name: Name of image; if not provided will name of first parent image, and if
              that is not available will use filename of path excluding extension; one
              of these must be available
            parents: Parent image(s) from which this image is descended
        """
        if image is None and path is None:
            raise ValueError(
                "PipeImage requires either an image or the path to an image; neither "
                "has been provided."
            )
        if image is not None and path is not None:
            raise ValueError(
                "PipeImage requires either an image or the path to an image; both "
                "have been provided."
            )
        self._image = image
        self.path = path

        if parents is not None:
            if isinstance(parents, PipeImage):
                parents = [parents]
            if not isinstance(parents, list):
                parents = list(parents)
        self._parents = parents

        if name is None:
            if self.parents is not None:
                self._name = self.parents[0].name
            elif self.path is not None:
                self._name = self.path.stem
            else:
                raise ValueError(
                    "PipeImage requires either a name, the path to an image whose "
                    "filename will be used as the name, or a parent image whose name "
                    "will be used."
                )

    def __repr__(self):
        return (
            f"<PipeImage '{self.name}' "
            f"of mode={self.image.mode} "
            f"and size={self.image.size} "
            f"and parents={self.count_parents()}>"
        )

    def count_parents(self):
        if self.parents is not None:
            return len(self.parents) + sum(p.count_parents() for p in self.parents)
        return 0

    @property
    def image(self) -> Image.Image:
        if self._image is None:
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
        return self._parents

    @property
    def path(self) -> Optional[Path]:
        return self._path

    @path.setter
    def path(self, value: Union[Path, str]) -> None:
        if isinstance(value, str):
            value = Path(validate_input_file(value))
        self._path = value

    @property
    def name(self) -> str:
        return self._name
