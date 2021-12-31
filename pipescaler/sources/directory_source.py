#!/usr/bin/env python
#   pipescaler/sources/directory_source.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Yields images from a directory"""
from __future__ import annotations

from typing import Any, List, Union

from pipescaler.common import validate_input_path
from pipescaler.core import Source, get_files


class DirectorySource(Source):
    """Yields images from a directory"""

    exclusions = {".DS_Store", "desktop"}

    def __init__(
        self,
        directory: Union[str, List[str]],
        exclusions: Union[str, List[str]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Validate and store static configuration

        Arguments:
            directory: Directory from which to yield files
            exclusions: Names of files to exclude
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        if exclusions is None:
            exclusions = set()
        exclusions |= self.exclusions

        # Store configuration
        if isinstance(directory, str):
            directory = [directory]
        self.directories = [
            validate_input_path(d, file_ok=False, directory_ok=True) for d in directory
        ]

        # Store list of filenames
        filenames = get_files(
            self.directories, style="absolute", exclusion_sources=exclusions
        )
        filenames = list(filenames)
        filenames.sort(key=self.sort, reverse=True)
        self.filenames = filenames

    def __iter__(self):
        """Yield next image"""
        for filename in self.filenames:
            yield filename

    @staticmethod
    def sort(filename):
        """Sort outfiles to be yielded by source"""
        return "".join([f"{ord(c):03d}" for c in filename.lower()])
