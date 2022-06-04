#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for sources."""
from abc import ABC, abstractmethod

from pipescaler.core.pipe.pipeline import Pipeline


class Source(ABC):
    """Abstract base class for sources."""

    def __iter__(self):
        """Iterator for images."""
        return self

    @abstractmethod
    def __next__(self):
        """Return next image."""
        raise NotImplementedError()

    def flow_into(self, *pipes):
        pipe = pipes[0]
        if len(self.outlets) != len(pipe.inlets):
            raise ValueError()
        print(pipes)
        return Pipeline()

    def flow_until_empty(self):
        try:
            while True:
                nay = next(self)
                print(f"{self}: {nay}")
        except StopIteration:
            pass

    @property
    def outlets(self) -> list[str]:
        """Outlets that flow out of source."""
        return ["outlet"]
