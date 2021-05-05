#!/usr/bin/env python
#   pipescaler/core/source.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from abc import ABC, abstractmethod
from os import walk
from os.path import dirname, join
from typing import Any, List, Optional

from PIL import Image

from pipescaler.common import (
    get_ext,
    get_name,
    validate_input_path,
    validate_output_path,
)

####################################### CLASSES ########################################
from pipescaler.core import PipeImage


class Source(ABC):

    # region Builtins

    def __init__(self, directory: str, **kwargs: Any) -> None:
        # Prepare attributes
        self.directory = validate_output_path(
            directory, file_ok=False, directory_ok=True
        )
        self.infiles = []
        for (dirpath, dirnames, filenames) in walk(self.directory):
            for file in filenames:
                if file != ".DS_Store":
                    self.infiles.append(join(dirpath, file))
        self.infiles.sort(key=self.sort)

        # Prepare name and description
        self.name = self.__class__.__name__.lower()
        self.desc = f"source {self.__class__.__name__} ({self.directory})"

    def __iter__(self):
        for infile in self.infiles:
            infile = validate_input_path(infile)
            name = get_name(infile)
            ext = get_ext(infile)
            image = Image.open(infile)
            relative_directory = (
                dirname(infile).replace(self.directory.rstrip("/"), "").lstrip("/")
            )
            yield PipeImage(infile, name, ext, image)

    def __repr__(self) -> str:
        return self.desc

    def __str__(self) -> str:
        return self.name

    # endregion

    # region Properties

    @property
    def inlets(self) -> Optional[List[str]]:
        return None

    @property
    def outlets(self) -> Optional[List[str]]:
        return ["outlet"]

    # endregion

    # region Static Methods

    @staticmethod
    @abstractmethod
    def sort(filename):
        raise NotImplementedError()

    # endregion
