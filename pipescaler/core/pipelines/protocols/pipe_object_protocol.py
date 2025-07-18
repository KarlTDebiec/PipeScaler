# Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
# and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Protocol for pipeline objects."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from pipescaler.common.typing import PathLike


@runtime_checkable
class PipeObjectProtocol(Protocol):
    """Protocol for pipeline objects."""

    @property
    def location_name(self) -> str:
        """Location relative to root directory and name."""
        ...

    def save(self, path: PathLike) -> None:
        """Save object to file."""
        ...
