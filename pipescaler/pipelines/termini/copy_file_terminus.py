#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Copies images to a defined output directory."""
from __future__ import annotations

from logging import info
from os import remove
from pathlib import Path
from shutil import copyfile
from typing import Union

import numpy as np
from PIL import Image

from pipescaler.common import validate_output_directory
from pipescaler.core.pipelines import PipeImage, Terminus


class CopyFileTerminus(Terminus):
    """Copies images to a defined output directory."""

    def __init__(self, directory: Union[Path, str]) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            directory: Directory to which to copy images
        """
        self.directory = Path(
            validate_output_directory(directory, create_directory=True)
        )
        self.observed_files = set()

    def __call__(self, input_image: PipeImage) -> None:
        suffix = input_image.path.suffix if input_image.path is not None else ".png"
        outfile = self.directory.joinpath(input_image.name).with_suffix(suffix)
        self.observed_files.add(outfile.name)
        if outfile.exists():
            existing_image = Image.open(outfile)
            if np.array_equal(input_image.image, existing_image):
                info(f"{self}: {outfile} unchanged; not overwritten")
            else:
                if input_image.path is not None:
                    copyfile(input_image.path, outfile)
                else:
                    input_image.image.save(outfile)
                info(f"{self}: {outfile} changed; overwritten")
        else:
            if input_image.path is not None:
                copyfile(input_image.path, outfile)
            else:
                input_image.image.save(outfile)
            info(f"{self}: '{outfile}' saved")

    def purge_unrecognized_files(self) -> None:
        for filepath in self.directory.iterdir():
            if filepath.name not in self.observed_files:
                remove(filepath)
                info(f"{self}: {filepath} removed")
