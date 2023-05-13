#!/usr/bin/env python
#  Copyright 2020-2023 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Copies images to an output directory."""
from __future__ import annotations

from datetime import datetime
from logging import info
from os import utime
from shutil import copyfile

import numpy as np
from PIL import Image

from pipescaler.core.pipelines import DirectoryTerminus
from pipescaler.image.core.pipelines import ImageTerminus, PipeImage


class ImageDirectoryTerminus(ImageTerminus, DirectoryTerminus):
    """Copies images to an output directory."""

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
            if input_image.path:
                copyfile(input_image.path, outfile)
            else:
                input_image.image.save(outfile)

        suffix = input_image.path.suffix if input_image.path else ".png"
        outfile = (self.directory / input_image.location_name).with_suffix(suffix)
        self.observed_files.add(str(outfile.relative_to(self.directory)))
        if outfile.exists():
            if (
                input_image.path
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
