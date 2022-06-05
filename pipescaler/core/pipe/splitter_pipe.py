#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for splitter pipes."""
from abc import ABC, abstractmethod
from typing import Any, Optional, Type

from pipescaler.core.pipe.pipe import Pipe
from pipescaler.core.stages import Splitter


class SplitterPipe(Pipe, ABC):
    """Abstract base class for splitter pipes."""

    def __init__(
        self, suffixes: Optional[dict[str, str]] = None, **kwargs: Any
    ) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            suffixes: Suffixes to add to split outfiles
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Store configuration
        self.suffixes = (
            suffixes
            if suffixes is not None
            else {outlet: outlet for outlet in self.outlets}
        )

        self.splitter_object = self.splitter(**kwargs)

    @property
    def inlets(self) -> list[str]:
        """Inlets that flow into pipe."""
        return ["inlet"]

    @classmethod
    @property
    @abstractmethod
    def splitter(cls) -> Type[Splitter]:
        """Type of splitter wrapped by pipe."""
        raise NotImplementedError()
