# Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
# and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Protocol for pipeline termini."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from pipescaler.core.pipelines.protocols.pipe_object_protocol import (
    PipeObjectProtocol,
)


@runtime_checkable
class TerminusProtocol[T: PipeObjectProtocol](Protocol):
    """Protocol for pipeline termini."""

    def __call__(self, input_obj: T) -> None:
        """Terminate object."""
        ...
