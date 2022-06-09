#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Checkpoint manager."""
from functools import wraps
from logging import info
from os import remove
from pathlib import Path
from typing import Callable

from pipescaler.common import validate_output_path
from pipescaler.core import PipeImage


class CheckpointManager:
    """Checkpoint manager."""

    def __init__(self, directory: str) -> None:
        """Validate and store configuration.

        Arguments:
            directory: Directory to which to copy images
        """
        self.directory = Path(
            validate_output_path(
                directory, file_ok=False, directory_ok=True, create_directory=True
            )
        )
        self.observed_files = set()

    def __repr__(self):
        return "<CheckpointManager>"

    def checkpoint(self, name: str) -> Callable[[PipeImage], PipeImage]:
        def checkpoint_decorator(function):
            @wraps(function)
            def wrapped(image: PipeImage) -> PipeImage:
                checkpoint_directory = self.directory.joinpath(image.name)
                checkpoint_directory.mkdir(exist_ok=True)
                checkpoint = checkpoint_directory.joinpath(name).with_suffix(".png")
                self.observed_files.add(checkpoint)
                if checkpoint.exists():
                    output_image = PipeImage(path=checkpoint, parents=image)
                    info(f"{self}: {image.name} checkpoint {checkpoint} loaded")
                else:
                    output_image = function(image)
                    output_image.image.save(checkpoint)
                    info(f"{self}: {image.name}'s checkpoint {checkpoint} saved")
                return output_image

            return wrapped

        return checkpoint_decorator

    def purge_unrecognized_files(self) -> None:
        for checkpoint_directory in self.directory.iterdir():
            for checkpoint in checkpoint_directory.iterdir():
                if checkpoint.is_file() and checkpoint not in self.observed_files:
                    remove(checkpoint)
                    info(f"{self}: '{checkpoint}' removed")
            if not any(checkpoint_directory.iterdir()):
                remove(checkpoint_directory)
                info(f"{self}: '{checkpoint_directory}' removed")
