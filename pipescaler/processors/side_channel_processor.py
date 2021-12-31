#!/usr/bin/env python
#   pipescaler/processors/side_channel_processor.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Replaces image with an alternative sourced from a defined directory"""
from __future__ import annotations

from logging import info
from os.path import basename, dirname, join, splitext
from shutil import copyfile, move
from typing import Any

from PIL import Image

from pipescaler.common import validate_input_path
from pipescaler.core import Processor, get_files


class SideChannelProcessor(Processor):
    """Replaces image with an alternative sourced from a defined directory."""

    def __init__(
        self,
        directory: str,
        clean_suffix: str = None,
        match_input_mode: bool = True,
        **kwargs: Any,
    ) -> None:
        """
        Validate and store static configuration

        Args:
            directory: Directory from which to load alternative images
            clean_suffix: Suffix to remove from alternative images
            match_input_mode: Ensure output alternative image matches mode of input
              image
            **kwargs: Additional keyword images
        """
        super().__init__(**kwargs)

        # Store configuration
        self.directory = validate_input_path(
            directory, file_ok=False, directory_ok=True, create_directory=True
        )
        self.side_files = {}
        for filename in get_files(self.directory, style="absolute"):
            filename_base, filename_extension = splitext(basename(filename))
            if clean_suffix is not None and filename_base.endswith(clean_suffix):
                filename_base = filename_base[: -len(clean_suffix)]
                clean_filename = join(
                    self.directory, f"{filename_base}{filename_extension}"
                )
                move(filename, clean_filename)
                info(f"{self}: '{filename}' renamed to '{clean_filename}'")
                filename = clean_filename
            self.side_files[filename_base] = filename
        self.match_input_mode = match_input_mode

    def process_file(self, infile: str, outfile: str) -> None:
        try:
            side_file = self.side_files[basename(dirname(infile))]
            if self.match_input_mode:
                input_image = Image.open(infile)
                side_image = Image.open(side_file)
                if side_image.mode != input_image.mode:
                    side_image = side_image.convert(input_image.mode)
                    side_image.save(side_file)
                    info(f"{self}: '{side_file}' updated to mode {side_image.mode}")
                side_image.save(outfile)
            else:
                copyfile(side_file, outfile)
            info(f"{self}: '{outfile}' saved")

        except KeyError:
            raise FileNotFoundError()
