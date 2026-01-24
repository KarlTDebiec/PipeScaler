#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for termini that write objects to an output directory."""

from __future__ import annotations

from abc import ABC
from logging import info
from os import remove, rmdir
from pathlib import Path

from pipescaler.common.validation import val_output_dir_path
from pipescaler.core.pipelines.terminus import Terminus


class DirectoryTerminus(Terminus, ABC):
    """Abstract base class for termini that write objects to an output directory."""

    def __init__(self, directory: Path | str):
        """Validate and store configuration and initialize.

        Arguments:
            directory: Directory to which to copy images
        """
        self.directory = val_output_dir_path(directory)
        self.observed_files: set[str] = set()

    def __repr__(self) -> str:
        """Representation."""
        return f"{self.__class__.__name__}(directory={self.directory!r})"

    def purge_unrecognized_files(self, directory: Path | None = None):
        """Remove unrecognized files and subdirectories in output directory."""
        if directory is None:
            directory = self.directory
        for path in directory.iterdir():
            if path.is_dir():
                self.purge_unrecognized_files(path)
            elif path.is_file():
                relative_path = path.relative_to(self.directory)
                if str(relative_path) not in self.observed_files:
                    remove(path)
                    info(f"{self}: '{relative_path}' removed")
            else:
                raise ValueError(f"Unsupported path type: {path}")
        if not any(directory.iterdir()) and directory != self.directory:
            rmdir(directory)
            info(f"{self}: directory '{directory.relative_to(self.directory)}' removed")
