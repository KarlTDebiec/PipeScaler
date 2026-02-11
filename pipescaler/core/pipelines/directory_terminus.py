#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for termini that write objects to an output directory."""

from __future__ import annotations

from abc import ABC
from logging import info
from os import remove, rmdir
from typing import TYPE_CHECKING

from pipescaler.common.validation import val_output_dir_path

from .pipe_object import PipeObject
from .terminus import Terminus

if TYPE_CHECKING:
    from pathlib import Path


class DirectoryTerminus[T: PipeObject](Terminus[T], ABC):
    """Abstract base class for termini that write objects to an output directory."""

    def __init__(self, dir_path: Path | str):
        """Validate and store configuration and initialize.

        Arguments:
            dir_path: Path to directory to which to copy images
        """
        self.dir_path = val_output_dir_path(dir_path)
        self.observed_files: set[str] = set()

    def __repr__(self) -> str:
        """Representation."""
        return f"{self.__class__.__name__}(dir_path={self.dir_path!r})"

    def purge_unrecognized_files(self, dir_path: Path | None = None):
        """Remove unrecognized files and subdirectories in output directory."""
        if dir_path is None:
            dir_path = self.dir_path
        for path in dir_path.iterdir():
            if path.is_dir():
                self.purge_unrecognized_files(path)
            elif path.is_file():
                relative_path = path.relative_to(self.dir_path)
                if str(relative_path) not in self.observed_files:
                    remove(path)
                    info(f"{self}: '{relative_path}' removed")
            else:
                raise ValueError(f"Unsupported path type: {path}")
        if not any(dir_path.iterdir()) and dir_path != self.dir_path:
            rmdir(dir_path)
            info(f"{self}: directory '{dir_path.relative_to(self.dir_path)}' removed")
