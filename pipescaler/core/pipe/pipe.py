#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Base class for pipes."""
from abc import ABC, abstractmethod
from typing import Any, Optional


class Pipe(ABC):
    def __init__(
        self, name: Optional[str] = None, desc: Optional[str] = None, **kwargs: Any
    ) -> None:
        """Validate and store configuration.

        Arguments:
            name: Name of pipe
            desc: Description of pipe
            **kwargs: Additional keyword arguments
        """
        self.name = name if name is not None else self.__class__.__name__
        self.desc = desc if desc is not None else self.name

    def __repr__(self) -> str:
        """Detailed representation of pipe."""
        return self.desc

    def __str__(self) -> str:
        """Simple representation of pipe."""
        return self.name

    @property
    @abstractmethod
    def inlets(self) -> list[str]:
        """Inlets that flow into pipe."""
        raise NotImplementedError()

    @property
    @abstractmethod
    def outlets(self) -> list[str]:
        """Outlets that flow out of pipe."""
        raise NotImplementedError()
