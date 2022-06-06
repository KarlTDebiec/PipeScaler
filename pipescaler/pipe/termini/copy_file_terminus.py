#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Copies images to a defined output directory."""
from __future__ import annotations

from logging import info
from pathlib import Path
from shutil import copyfile
from typing import Any

from pipescaler.common import validate_output_path
from pipescaler.core import PipeImage
from pipescaler.core.stages import Terminus


class CopyFileTerminus(Terminus):
    """Copies images to a defined output directory."""

    def __init__(self, directory: str, purge: bool = False, **kwargs: Any) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            directory: Directory to which to copy images
            purge: Purge pre-existing files from directory
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Store configuration
        self.directory = Path(
            validate_output_path(
                directory, file_ok=False, directory_ok=True, create_directory=True
            )
        )

    def __call__(self, input_pipe_image: PipeImage) -> None:
        infile = ""
        outfile = ""
        info(f"{self}: '{outfile}' saved")
        copyfile(infile, outfile)
        # TODO: Track file creation

        # TODO: Re-implement once lazy loading and checkpoints are implemented
        # if isfile(outfile):
        #     infile_md5sum = md5(open(infile, "rb").read()).hexdigest()
        #     outfile_md5sum = md5(open(outfile, "rb").read()).hexdigest()
        #     if infile_md5sum == outfile_md5sum:
        #         info(f"{self}: '{outfile}' unchanged; not overwritten")
        #     else:
        #     info(f"{self}: '{outfile}' changed; overwritten")

    def purge_unrecognized_files(self):
        pass
        # TODO: Re-implement to track files creation/checking
        # if purge:
        #     for filename in get_files(self.directory, style="absolute"):
        #         remove(filename)
        #         info(f"{self}: '{filename}' removed")
