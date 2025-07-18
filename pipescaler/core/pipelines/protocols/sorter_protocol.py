# Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
# and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Protocol for sorters."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from pipescaler.core.pipelines.protocols.pipe_object_protocol import (
    PipeObjectProtocol,
)


@runtime_checkable
class SorterProtocol[T: PipeObjectProtocol](Protocol):
    """Protocol for sorters."""

    def __call__(self, obj: T) -> str | None:
        """Get the outlet to which an object should be sorted."""
        ...

    @property
    def outlets(self) -> tuple[str, ...]:
        """Outlets to which objects may be sorted."""
        ...
