#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Image within a pipeline"""
from __future__ import annotations

from os.path import basename, dirname, join, splitext
from typing import Optional


class PipeImage:
    """Image within a pipeline"""

    def __init__(self, absolute_path: str, parent: PipeImage = None) -> None:
        """
        Validate and store static configuration

        Arguments:
            absolute_path: Path to image file
            parent: Parent image from which this image is descended
        """
        self.absolute_filename = absolute_path
        self.directory = dirname(self.absolute_filename)
        self.full_filename = basename(self.absolute_filename)
        self.base_filename = splitext(self.full_filename)[0]
        self.extension = splitext(self.full_filename)[1].lstrip(".")

        self.parent = parent
        if self.parent is None:
            self.name = self.base_filename
        else:
            self.name = self.parent.name

    def __repr__(self) -> str:
        """Detailed representation of image"""
        return self.base_filename

    def __str__(self) -> str:
        """Simple representation of image"""
        return self.base_filename

    def get_child(
        self,
        directory: str,
        suffix: str,
        trim_suffixes: Optional[list[str]] = None,
        extension="png",
    ) -> PipeImage:
        """
        Get a new PipeImage descended from this one

        Arguments:
            directory: Directory in which to place child image's path
            suffix: Suffix to append to child image's name
            trim_suffixes: Suffixes to trim from child image's name if present in parent
            extension: Extension to use for child image

        Returns:
            New PipeImage descended from this one
        """
        filename = self.base_filename
        if filename.startswith(self.name):
            filename = filename[len(self.name) :]

        if trim_suffixes is not None:
            for trim_suffix in trim_suffixes:
                if trim_suffix in filename:
                    filename = filename[: filename.rindex(trim_suffix)]
                    break
            filename = filename.rstrip("_")

        return PipeImage(
            join(directory, f"{filename}_{suffix}.{extension}".lstrip("_")), self
        )
