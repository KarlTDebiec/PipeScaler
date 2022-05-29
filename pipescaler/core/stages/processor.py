#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for processors."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional

from pipescaler.core.stage import Stage


class Processor(Stage, ABC):
    """Abstract base class for processors."""

    def __init__(self, suffix: Optional[str] = None, **kwargs: Any) -> None:
        """Validate and store configuration.

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

    @abstractmethod
    def __call__(self, infile: str, outfile: str) -> None:
        """Read image from infile, process it, and save to outfile.

        Arguments:
            infile: Input file path
            outfile: Output file path
        """
        raise NotImplementedError()

    @property
    def inlets(self) -> list[str]:
        """Inlets that flow into stage."""
        return ["inlet"]

    @property
    def outlets(self) -> list[str]:
        """Outlets that flow out of stage."""
        return ["outlet"]