#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Scans directories for new files."""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence
from itertools import chain
from logging import debug, info
from os import remove, rmdir
from os.path import expandvars
from pathlib import Path
from shutil import copy, move

from PIL import Image

from pipescaler.common import DirectoryNotFoundError
from pipescaler.common.validation import validate_input_directories


class FileScanner:
    """Scans directories for new files."""

    exclusions = {".DS_Store", "desktop"}

    def __init__(
        self,
        input_directories: Path | str | Iterable[Path | str],
        project_root: Path | str,
        reviewed_directories: Path | str | list[Path | str] | None,
        rules: list[tuple[str, str]] | None = None,
        *,
        remove_prefix: str | None = None,
        output_format: str | None = None,
    ) -> None:
        """Validate configuration and initialize.

        Arguments:
            input_directories: Directory or directories from which to read input files
            project_root: Root directory of project
            reviewed_directories: Directory or directories of reviewed files
            rules: Rules by which to process images
            remove_prefix: Prefix to remove from output file names
            output_format: Format of output files
        """
        super().__init__()

        def get_names(directories: Path | Sequence[Path]) -> set[str]:
            """Get names of files in directories.

            Arguments:
                directories: Directory or directories of input files
            Returns:
                Set of file names
            """
            if isinstance(directories, Path):
                directories = [directories]
            files = chain.from_iterable(d.iterdir() for d in directories)
            names = {f.stem for f in files}

            return names

        # Validate input and output directory and file paths
        self.input_directories = validate_input_directories(input_directories)
        """Directories from which to read input files."""

        project_root = Path(expandvars(project_root)).resolve()
        self.ignore_directory = project_root / "ignore"
        """Directory of images to ignore if present in input directories."""
        self.copy_directory = project_root / "new"
        """Directory to which to copy images that match 'copy' rule."""
        self.move_directory = project_root / "review"
        """Directory to which to move images that match 'move' rule."""
        self.remove_directory = project_root / "remove"
        """Directory of images that should be removed from input directories."""

        self.reviewed_directories = None
        """Directories of files that have been reviewed."""
        if reviewed_directories:
            try:
                self.reviewed_directories = validate_input_directories(
                    reviewed_directories
                )
            except DirectoryNotFoundError:
                self.reviewed_directories = []

        # Prepare filename data structures
        self.reviewed_names: set[str] = set()
        """Names of images that have been reviewed."""
        if self.reviewed_directories:
            self.reviewed_names = get_names(self.reviewed_directories)

        self.ignored_names: set[str] = set()
        """Names of images to ignore."""
        if self.ignore_directory.exists():
            self.ignored_names = get_names(self.ignore_directory)

        # Prepare rules
        self.rules = None
        """Rules by which to classify images."""
        if rules:
            self.rules = [(re.compile(regex), action) for regex, action in rules]

        # Prepare output configuration
        self.remove_prefix = remove_prefix
        """Prefix to remove from output file names."""
        self.output_format = output_format
        """Format of output files."""
        if output_format and not output_format.startswith("."):
            self.output_format = f".{output_format}"

    def __call__(self) -> None:
        """Perform operations."""
        self.clean_project_root()

        for input_directory in self.input_directories:
            for file_path in input_directory.iterdir():
                self.perform_operation(file_path)

    def clean_project_root(self) -> None:
        """Clean project root copy and remove directories."""
        if self.copy_directory.exists():
            for file_path in self.copy_directory.iterdir():
                remove(file_path)
                info(f"'{file_path}' removed")
            rmdir(self.copy_directory)
            info(f"'{self.copy_directory}' removed")

        if self.remove_directory.exists():
            for file_path in self.remove_directory.iterdir():
                name = file_path.name
                if self.remove_prefix:
                    name = f"{self.remove_prefix}{name}"
                for input_directory in self.input_directories:
                    for match in input_directory.glob(f"{Path(name).stem}.*"):
                        remove(match)
                        info(f"'{match}' removed")
                remove(file_path)
                info(f"'{file_path}' removed")
            rmdir(self.remove_directory)
            info(f"'{self.remove_directory}' removed")

    def copy(self, file_path: Path) -> None:
        """Copy file to copy directory.

        Arguments:
            file_path: Path to file to copy
        """
        if not self.copy_directory.exists():
            self.copy_directory.mkdir(parents=True)
            info(f"'{self.copy_directory}' created")

        output_name = file_path.name
        if self.remove_prefix:
            output_name = output_name.removeprefix(self.remove_prefix)

        output_path = self.copy_directory / output_name
        if self.output_format:
            output_path = output_path.with_suffix(self.output_format)

        if self.output_format is None:
            copy(file_path, output_path)
        else:
            with Image.open(file_path) as image:
                image.save(output_path)

    def get_operation(self, name: str) -> str:
        """Select operation for filename.

        Arguments:
            name: Name of file
        Returns:
            Operation to perform
        """
        if self.remove_prefix:
            name = name.removeprefix(self.remove_prefix)
        if name in self.reviewed_names:
            return "known"
        if name in self.ignored_names:
            return "ignore"
        if self.rules:
            for regex, status in self.rules:
                if regex.match(name):
                    return status

        return "copy"

    def move(self, file_path: Path) -> None:
        """Move file to review directory.

        Arguments:
            file_path: Path to file to move
        """
        if not self.move_directory.exists():
            self.move_directory.mkdir(parents=True)
            info(f"'{self.move_directory}' created")

        output_name = file_path.name
        if self.remove_prefix:
            output_name = output_name.removeprefix(self.remove_prefix)

        output_path = self.move_directory / output_name
        if self.output_format:
            output_path = output_path.with_suffix(self.output_format)

        if self.output_format is None:
            move(file_path, output_path)
        else:
            with Image.open(file_path) as image:
                image.save(output_path)
            remove(file_path)

    def perform_operation(self, file_path: Path) -> None:
        """Perform operations for filename.

        Arguments:
            file_path: Path to file
        """
        operation = self.get_operation(file_path.stem)

        match operation:
            case "known":
                debug(f"'{file_path.stem}' known")
            case "ignore":
                debug(f"'{file_path.stem}' ignored")
            case "remove":
                remove(file_path)
                info(f"'{file_path.stem}' removed")
            case "copy":
                self.copy(file_path)
                info(f"'{file_path.stem}' copied")
            case "move":
                self.move(file_path)
                info(f"'{file_path.stem}' moved")
            case _:
                raise ValueError(f"Unknown operation '{operation}'")
