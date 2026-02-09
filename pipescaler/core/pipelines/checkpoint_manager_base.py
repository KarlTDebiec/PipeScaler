#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for checkpoint managers."""

from __future__ import annotations

from abc import ABC
from collections.abc import Sequence
from logging import warning
from pathlib import Path
from platform import system
from typing import TYPE_CHECKING

from pipescaler.common.exception import UnsupportedPlatformError
from pipescaler.common.validation import val_output_dir_path

if TYPE_CHECKING:
    from .pipe_object import PipeObject


class CheckpointManagerBase(ABC):
    """Abstract base class for checkpoint managers."""

    SUPPORTED_MTIME_SYSTEMS = frozenset(("Darwin", "Linux", "Windows"))
    """Operating systems supported for mtime-based checkpoint validation."""

    def __init__(self, dir_path: Path | str, *, validate_input_mtime: bool = False):
        """Initialize.

        Arguments:
            dir_path: Path to directory in which to store checkpoints
            validate_input_mtime: Whether to require checkpoint mtimes to be newer than
              or equal to input mtimes before loading from checkpoint
        """
        self.dir_path = val_output_dir_path(dir_path)
        """Path to directory in which to store checkpoints."""
        self.validate_input_mtime = validate_input_mtime
        """Whether checkpoint validity is based on mtime and existence."""
        self.observed_checkpoints: set[tuple[str, str]] = set()
        """Observed checkpoints as tuples of image and checkpoint names."""

    def __repr__(self) -> str:
        """Representation."""
        return (
            f"{self.__class__.__name__}("
            f"dir_path={self.dir_path!r}, "
            f"validate_input_mtime={self.validate_input_mtime!r})"
        )

    def __str__(self) -> str:
        """String representation."""
        return f"<{self.__class__.__name__}>"

    def observe(self, location_name: str, cpt: str):
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

    def checkpoints_current(
        self, inputs: Sequence[PipeObject], cpt_paths: Sequence[Path]
    ) -> bool:
        """Assess whether checkpoints are current for a collection of inputs.

        Arguments:
            inputs: Input objects whose source files determine checkpoint freshness
            cpt_paths: Paths to checkpoints to assess
        Returns:
            Whether all checkpoints should be treated as current
        """
        if not self.validate_input_mtime:
            return True

        sysname = system()
        if sysname not in self.SUPPORTED_MTIME_SYSTEMS:
            raise UnsupportedPlatformError(
                "Input mtime checkpoint validation is unsupported on "
                f"'{sysname}'; supported operating systems are "
                f"{sorted(self.SUPPORTED_MTIME_SYSTEMS)!r}."
            )

        if len(inputs) == 0:
            raise ValueError("At least one input object is required.")

        if len(cpt_paths) == 0:
            raise ValueError("At least one checkpoint path is required.")

        input_paths: list[Path] = []
        for input_obj in inputs:
            if input_obj.path is None:
                return False
            input_paths.append(input_obj.path)

        try:
            latest_input_mtime_ns = max(path.stat().st_mtime_ns for path in input_paths)
            earliest_checkpoint_mtime_ns = min(
                cpt_path.stat().st_mtime_ns for cpt_path in cpt_paths
            )
        except OSError:
            warning(
                f"{self}: unable to stat one or more input/checkpoint paths; "
                "treating checkpoints as stale."
            )
            return False

        return earliest_checkpoint_mtime_ns >= latest_input_mtime_ns
