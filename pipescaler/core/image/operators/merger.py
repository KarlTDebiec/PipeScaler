#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for mergers."""
from __future__ import annotations

from abc import ABC, abstractmethod

from PIL import Image

from pipescaler.core.image.operator import Operator


class Merger(Operator, ABC):
    """Abstract base class for mergers."""

    @abstractmethod
    def __call__(self, *input_images: Image.Image) -> Image.Image:
        raise NotImplementedError()