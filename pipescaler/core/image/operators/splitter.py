#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for splitters."""
from __future__ import annotations

from abc import ABC, abstractmethod

from PIL import Image

from pipescaler.core.image.operator import Operator


class Splitter(Operator, ABC):
    """Abstract base class for splitters."""

    @abstractmethod
    def __call__(self, input_image: Image.Image) -> tuple[Image.Image, ...]:
        raise NotImplementedError()
