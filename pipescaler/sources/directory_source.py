#!/usr/bin/env python
#   pipescaler/sources/directory_source.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from typing import Any, List, Union

from pipescaler.common import validate_input_path
from pipescaler.core import Source, parse_file_list


####################################### CLASSES ########################################
class DirectorySource(Source):
    exclusions = {".DS_Store", "desktop"}

    # region Builtins

    def __init__(
        self, directory: str, exclusions: Union[str, List[str]] = None, **kwargs: Any
    ) -> None:
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
        filenames = parse_file_list(self.directories, True, exclusions)
        filenames = list(filenames)
        filenames.sort(key=self.sort, reverse=True)
        self.filenames = filenames

    def __iter__(self):
        for filename in self.filenames:
            yield filename

    # endregion

    # region Static Methods

    @staticmethod
    def sort(filename):
        return "".join([f"{ord(c):03d}" for c in filename.lower()])

    # endregion
