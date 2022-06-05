#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for processor pipes."""
from abc import ABC, abstractmethod
from typing import Any, Optional, Type

from pipescaler.core.pipe.pipe import Pipe
from pipescaler.core.stages import Processor


class ProcessorPipe(Pipe, ABC):
    """Abstract base class for processor pipes."""

    def __init__(self, suffix: Optional[str] = None, **kwargs: Any) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            suffix: Suffix to append to images
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Store configuration
        if suffix is not None:
            self.suffix = suffix
        else:
            self.suffix = self.name

        self.processor_object = self.processor(**kwargs)

    @property
    def inlets(self) -> list[str]:
        """Inlets that flow into pipe."""
        return ["inlet"]

    @property
    def outlets(self) -> list[str]:
        """Outlets that flow out of pipe."""
        return ["outlet"]

    @classmethod
    @property
    @abstractmethod
    def processor(cls) -> Type[Processor]:
        """Type of processor wrapped by pipe."""
        raise NotImplementedError()
