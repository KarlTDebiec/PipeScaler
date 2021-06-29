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

from os import listdir
from typing import Any

from pipescaler.common import validate_input_path
from pipescaler.core import Source


####################################### CLASSES ########################################
class DirectorySource(Source):
    skip_files = [".DS_Store"]

    # region Builtins

    def __init__(self, directory: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        # Store configuration
        self.directory = validate_input_path(
            directory, file_ok=False, directory_ok=True
        )

    def __iter__(self):
        filenames = [
            validate_input_path(f, default_directory=self.directory)
            for f in listdir(self.directory)
            if f not in self.skip_files
        ]
        filenames.sort(key=self.sort)

        for filename in filenames:
            yield {"outlet": filename}

    # endregion

    # region Static Methods

    @staticmethod
    def sort(filename):
        return "".join([f"{ord(c):03d}" for c in filename.lower()])

    # endregion
