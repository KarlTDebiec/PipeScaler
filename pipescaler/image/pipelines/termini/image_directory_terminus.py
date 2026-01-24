#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
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

    def __call__(self, input_obj: PipeImage):
        """Save image to output directory.

        If image already exists within output directory, checks if it should be
        overwritten. If pre-existing image is newer, or pre-existing image's contents
        are the same as the incoming image, does not overwrite.

        Arguments:
            input_obj: Image to save to output directory
        """

        def save_image():
            """Save image, by copying file if possible."""
            if not self.directory.exists():
                self.directory.mkdir(parents=True)
                info(f"{self}: '{self.directory}' created")
            if not output_path.parent.exists():
                output_path.parent.mkdir(parents=True)
                info(
                    f"{self}: "
                    f"'{output_path.parent.relative_to(self.directory)}' created"
                )
            if input_obj.path:
                copyfile(input_obj.path, output_path)
            else:
                input_obj.image.save(output_path)

        suffix = input_obj.path.suffix if input_obj.path else ".png"
        output_path = (self.directory / input_obj.location_name).with_suffix(suffix)
        self.observed_files.add(str(output_path.relative_to(self.directory)))
        if output_path.exists():
            if (
                input_obj.path
                and output_path.stat().st_mtime > input_obj.path.stat().st_mtime
            ):
                info(f"{self}: '{output_path}' is newer; not overwritten")
                return
            if np.array_equal(
                np.array(input_obj.image), np.array(Image.open(output_path))
            ):
                info(f"{self}: '{output_path}' unchanged; not overwritten")
                epoch = datetime.now().timestamp()
                utime(output_path, (epoch, epoch))
                info(f"{self}: '{output_path}' timestamp updated")
                return
            save_image()
            info(f"{self}: '{output_path}' changed; overwritten")
            return
        save_image()
        info(f"{self}: '{output_path}' saved")
