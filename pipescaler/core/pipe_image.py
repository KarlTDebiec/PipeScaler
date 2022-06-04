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
        image: Image,
        parent: Union[PipeImage, list[PipeImage]] = None,
    ) -> None:
        """Validate and store configuration.

        Arguments:
            image: Image
            parent: Parent from which this image is descended
        """
        self.image = image
        self.parent = parent

    def filename(self):
        raise NotImplementedError()
