#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for termini."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterator

from pipescaler.core import PipeImage


class Terminus(ABC):
    """Abstract base class for termini."""

    def __call__(self, inlet: Iterator[PipeImage]) -> None:
        for input_pipe_image in inlet:
            self.terminate(input_pipe_image)

    @abstractmethod
    def terminate(self, input_pipe_image: PipeImage) -> None:
        raise NotImplementedError()
