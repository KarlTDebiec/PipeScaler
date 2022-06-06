#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for sources."""
from abc import ABC, abstractmethod


class Source(ABC):
    """Abstract base class for sources."""

    def __iter__(self):
        """Iterator for images."""
        return self

    @abstractmethod
    def __next__(self):
        """Return next image."""
        raise NotImplementedError()
