#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Copies images to a defined output directory."""
from __future__ import annotations

from datetime import datetime
from logging import info
from os import remove, rmdir, utime
from pathlib import Path
from shutil import copyfile
from typing import Optional

import numpy as np
from PIL import Image

from pipescaler.common import PathLike, validate_output_directory
from pipescaler.core.pipelines import PipeImage, Terminus


class CopyFileTerminus(Terminus):
    """Copies images to a defined output directory."""

    def __init__(self, directory: PathLike) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            directory: Directory to which to copy images
        """
        self.directory = validate_output_directory(directory)
        self.observed_files: set[str] = set()

    def __call__(self, input_image: PipeImage) -> None:
        """Save image to output directory.

        If image already exists within output directory, checks if it should be
        overwritten. If pre-existing image is newer, or pre-existing image's contents
        are the same as the incoming image, does not overwrite.

        Arguments:
            input_image: Image to save to output directory
        """

        def save_image():
            """Save image, by copying file if possible."""
            if not self.directory.exists():
                self.directory.mkdir(parents=True)
                info(f"{self}: '{self.directory}' created")
            if not outfile.parent.exists():
                outfile.parent.mkdir(parents=True)
                info(f"{self}: '{outfile.parent.relative_to(self.directory)}' created")
            if input_image.path is not None:
                copyfile(input_image.path, outfile)
            else:
                input_image.image.save(outfile)

        suffix = input_image.path.suffix if input_image.path is not None else ".png"
        outfile = (self.directory / input_image.location_name).with_suffix(suffix)
        self.observed_files.add(str(outfile.relative_to(self.directory)))
        if outfile.exists():
            if (
                input_image.path is not None
                and outfile.stat().st_mtime > input_image.path.stat().st_mtime
            ):
                info(f"{self}: '{outfile}' is newer; not overwritten")
                return
            if np.array_equal(
                np.array(input_image.image), np.array(Image.open(outfile))
            ):
                info(f"{self}: '{outfile}' unchanged; not overwritten")
                epoch = datetime.now().timestamp()
                utime(outfile, (epoch, epoch))
                info(f"{self}: '{outfile}' timestamp updated")
                return
            save_image()
            info(f"{self}: '{outfile}' changed; overwritten")
            return
        save_image()
        info(f"{self}: '{outfile}' saved")

    def __repr__(self):
        """Representation."""
        return f"{self.__class__.__name__}(directory={self.directory})"

    def purge_unrecognized_files(self, directory: Optional[Path] = None) -> None:
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
