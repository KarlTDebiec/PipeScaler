# Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
# and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Protocol for pipeline segments."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from pipescaler.core.pipelines.protocols.pipe_object_protocol import (
    PipeObjectProtocol,
)


@runtime_checkable
class SegmentProtocol[T: PipeObjectProtocol](Protocol):
    """Protocol for pipeline segments."""

    def __call__(self, *input_objs: T) -> tuple[T, ...]:
        """Return output objects."""
        ...
