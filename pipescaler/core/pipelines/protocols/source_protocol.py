# Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
# and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Protocol for pipeline sources."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Protocol, runtime_checkable

from pipescaler.core.pipelines.protocols.pipe_object_protocol import (
    PipeObjectProtocol,
)


@runtime_checkable
class SourceProtocol[T: PipeObjectProtocol](Protocol):
    """Protocol for pipeline sources."""

    def __iter__(self) -> Iterator[T]:
        """Return iterator for objects."""
        ...

    def __next__(self) -> T:
        """Return next object."""
        ...
