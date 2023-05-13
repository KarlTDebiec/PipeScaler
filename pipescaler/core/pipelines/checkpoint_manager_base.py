#  Copyright 2020-2023 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for checkpoint managers."""
from __future__ import annotations

from abc import ABC
from logging import warning

from pipescaler.common import PathLike, validate_output_directory


class CheckpointManagerBase(ABC):
    """Abstract base class for checkpoint managers."""

    def __init__(self, directory: PathLike) -> None:
        """Initialize.

        Arguments:
            directory: Directory in which to store checkpoints
        """
        self.directory = validate_output_directory(directory)
        """Directory in which to store checkpoints."""
        self.observed_checkpoints: set[tuple[str, str]] = set()
        """Observed checkpoints as tuples of image and checkpoint names."""

    def __repr__(self) -> str:
        """Representation."""
        return f"{self.__class__.__name__}(directory={self.directory!r})"

    def __str__(self) -> str:
        """String representation."""
        return f"<{self.__class__.__name__}>"

    def observe(self, location_name: str, cpt: str) -> None:
        """Log observation of a checkpoint.

        Strips trailing '.' from relative_name because Windows does not support
        directory names with trailing periods.

        Arguments:
            location_name: Location and name of image
            cpt: Checkpoint name
        """
        if location_name.endswith("."):
            warning(
                f"{self}: '{location_name}' has trailing '.', which is not supported "
                f"for directories on Windows; stripping trailing '.' from checkpoint "
                f"directory name."
            )
            location_name = location_name.rstrip(".")
        self.observed_checkpoints.add((location_name, cpt))
