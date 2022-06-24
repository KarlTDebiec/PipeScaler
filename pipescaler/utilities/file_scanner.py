#!/usr/bin/env python
#  Copyright (C) 2020-2022. Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""FileScanner."""
from __future__ import annotations

import re
from itertools import chain
from logging import debug, info, warning
from os import remove, rmdir
from pathlib import Path
from shutil import copy, move
from typing import Optional, Sequence, Union

from PIL import Image

from pipescaler.common import DirectoryNotFoundError
from pipescaler.core import Utility


class FileScanner(Utility):
    """FileScanner."""

    exclusions = {".DS_Store", "desktop"}

    def __init__(
        self,
        project_root: Path,
        input_directories: Union[Path, list[Path]],
        reviewed_directories: Optional[Union[Path, list[Path]]],
        rules: Optional[list[tuple[str, str]]] = None,
        remove_prefix: Optional[str] = None,
        output_format: Optional[str] = None,
    ) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            project_root: Root directory of project
            input_directories: Directory or directories from which to read input files
            reviewed_directories: Directory or directories of reviewed files
            rules: Rules by which to process images
            remove_prefix: Prefix to remove from output file names
            output_format: Format of output files
        """
        super().__init__()

        def validate_input_directories(
            directories: Union[Path, Sequence[Path]]
        ) -> list[Path]:
            """Validate input directory paths and make them absolute.

            Arguments:
                directories: Directory or directories of input files
            Returns:
                List of absolute directory paths
            """
            if isinstance(directories, Path):
                directories = [directories]
            validated_directories = []
            for directory in directories:
                directory = directory.absolute()
                if directory.exists():
                    validated_directories.append(directory)
                else:
                    warning(f"{self}: Input directory '{directory}' does not exist")
            if len(validated_directories) == 0:
                raise DirectoryNotFoundError(
                    f"No directories provided in '{directories}' exist"
                )

            return validated_directories

        def get_names(directories: Union[Path, Sequence[Path]]) -> set[str]:
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
        self.ignore_directory = project_root.joinpath("ignore")
        """Directory of images to ignore if present in input directories."""
        self.copy_directory = project_root.joinpath("new")
        """Directory to which to copy images that match 'copy' rule."""
        self.move_directory = project_root.joinpath("review")
        """Directory to which to move images that match 'move' rule."""
        self.remove_directory = project_root.joinpath("remove")
        """Directory of images that should be removed from input directories."""
        self.input_directories = validate_input_directories(input_directories)
        """Directories from which to read input files."""
        self.reviewed_directories = None
        """Directories of files that have been reviewed."""
        if reviewed_directories is not None:
            self.reviewed_directories = validate_input_directories(reviewed_directories)

        # Prepare filename data structures
        self.reviewed_names = {}
        """Names of images that have been reviewed."""
        if self.reviewed_directories is not None:
            self.reviewed_names = get_names(self.reviewed_directories)

        self.ignored_names = {}
        """Names of images to ignore."""
        if self.ignore_directory.exists():
            self.ignored_names = get_names(self.ignore_directory)

        # Prepare rules
        self.rules = None
        """Rules by which to classify images."""
        if rules is not None:
            self.rules = [(re.compile(regex), action) for regex, action in rules]

        # Prepare output configuration
        self.remove_prefix = remove_prefix
        """Prefix to remove from output file names."""
        self.output_format = output_format
        """Format of output files."""
        if output_format is not None and not output_format.startswith("."):
            self.output_format = f".{output_format}"

    def __call__(self) -> None:
        """Perform operations."""
        # Prepare to for run
        if self.copy_directory.exists():
            for file_path in self.copy_directory.iterdir():
                remove(file_path)
                info(f"'{file_path}' removed")
            rmdir(self.copy_directory)
            info(f"{self}: '{self.copy_directory}' removed")
        if self.remove_directory.exists():
            for file_path in self.remove_directory.iterdir():
                name = file_path.name
                if self.remove_prefix is not None:
                    name = f"{self.remove_prefix}{name}"
                for input_directory in self.input_directories:
                    for match in input_directory.glob(f"{Path(name).stem}.*"):
                        remove(match)
                        info(f"{self}: '{match}' removed")
                remove(file_path)
                info(f"{self}: '{file_path}' removed")
            rmdir(self.remove_directory)
            info(f"{self}: '{self.remove_directory}' removed")

        # Perform operations
        for input_directory in self.input_directories:
            for file_path in input_directory.iterdir():
                self.perform_operation(file_path)

    def get_operation(self, name: str) -> str:
        """Select operation for filename.

        Arguments:
            name: Name of file
        Returns:
            Operation to perform
        """
        if self.remove_prefix is not None:
            name = name.removeprefix(self.remove_prefix)
        if name in self.reviewed_names:
            return "known"
        if name in self.ignored_names:
            return "ignore"
        if self.rules is not None:
            for regex, status in self.rules:
                if regex.match(name):
                    return status

        return "copy"

    def copy(self, file_path: Path) -> None:
        """Copy file to copy directory.

        Arguments:
            file_path: Path to file to copy
        """
        if not self.copy_directory.exists():
            self.copy_directory.mkdir(parents=True)
            info(f"{self}: '{self.copy_directory}' created")

        output_name = file_path.name
        if self.remove_prefix is not None:
            output_name = output_name.removeprefix(self.remove_prefix)

        output_path = self.copy_directory.joinpath(output_name)
        if self.output_format is not None:
            output_path = output_path.with_suffix(self.output_format)

        if self.output_format is None:
            copy(file_path, output_path)
        else:
            with Image.open(file_path) as image:
                image.save(output_path)

    def move(self, file_path: Path) -> None:
        """Move file to review directory.

        Arguments:
            file_path: Path to file to move
        """
        if not self.move_directory.exists():
            self.move_directory.mkdir(parents=True)
            info(f"{self}: '{self.move_directory}' created")

        output_name = file_path.name
        if self.remove_prefix is not None:
            output_name = output_name.removeprefix(self.remove_prefix)

        output_path = self.copy_directory.joinpath(output_name)
        if self.output_format is not None:
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
        if (operation := self.get_operation(file_path.stem)) == "known":
            debug(f"{self}: '{file_path.stem}' known")
        elif operation == "ignore":
            debug(f"{self}: '{file_path.stem}' ignored")
        elif operation == "remove":
            remove(file_path)
            info(f"'{self}: {file_path.stem}' removed")
        elif operation == "copy":
            self.copy(file_path)
            info(f"'{self}: {file_path.stem}' copied")
        elif operation == "move":
            self.move(file_path)
            info(f"'{self}: {file_path.stem}' moved")
        else:
            raise ValueError(f"{self}: Unknown operation '{operation}'")
