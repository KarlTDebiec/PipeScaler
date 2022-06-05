#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Image within a pipeline."""
from __future__ import annotations

from typing import Union

from PIL import Image


class PipeImage:
    """Image within a pipeline."""

    def __init__(
        self,
        image: Image.Image,
        parent: Union[PipeImage, list[PipeImage]] = None,
    ) -> None:
        """Validate and store configuration.

        Arguments:
            image: Image
            parent: Parent from which this image is descended
        """
        self.image = image
        self.parent = parent

    def __repr__(self):
        return f"PipeImage of mode {self.image.mode} and size {self.image.size} with {self.count_parents()} parents"

    def count_parents(self):
        if isinstance(self.parent, PipeImage):
            return 1 + self.parent.count_parents()
        elif isinstance(self.parent, list):
            return len(self.parent) + sum([p.count_parents() for p in self.parent])
        return 0

    def filename(self):
        raise NotImplementedError()
