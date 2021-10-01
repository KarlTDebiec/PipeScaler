#!/usr/bin/env python
#   pipescaler/core/pipe_image.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
from __future__ import annotations

from os.path import basename, dirname, join, splitext
from typing import List, Optional

from pipescaler.common import validate_output_path


class PipeImage:
    def __init__(self, path: str, parent: PipeImage = None) -> None:
        self.full_path = validate_output_path(path)
        self.directory = dirname(self.full_path)
        self.filename = splitext(basename(self.full_path))[0]
        self.extension = splitext(basename(self.full_path))[1].lstrip(".")

        self.parent = parent
        if self.parent is None:
            self.name = self.filename
        else:
            self.name = self.parent.name

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name

    def get_child(
        self,
        directory: str,
        suffix: str,
        trim_suffixes: Optional[List[str]] = None,
        extension="png",
    ) -> PipeImage:
        filename = self.filename
        if filename.startswith(self.name):
            filename = filename[len(self.name) :]

        if trim_suffixes is not None:
            for trim_suffix in trim_suffixes:
                if trim_suffix in filename:
                    prefix = filename[: filename.rindex(trim_suffix)]
                    break
            filename = filename.rstrip("_")

        return PipeImage(
            join(directory, f"{filename}_{suffix}.{extension}".lstrip("_")), self
        )
