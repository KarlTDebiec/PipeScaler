#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Checkpoint manager."""
from functools import wraps
from logging import info
from os import remove
from os.path import join
from pathlib import Path
from typing import Callable, Union

from pipescaler.common import validate_output_path
from pipescaler.core import PipeImage


class CheckpointManager:
    """Checkpoint manager."""

    def __init__(self, directory: Union[Path, str]) -> None:
        """Validate and store configuration.

        Arguments:
            directory: Directory to which to copy images
        """
        self.directory = Path(
            validate_output_path(
                directory, file_ok=False, directory_ok=True, create_directory=True
            )
        )
        self.image_names = set()
        self.checkpoint_names = set()

    def __repr__(self):
        return "<CheckpointManager>"

    def get_checkpoint(self, image: PipeImage, name: str) -> Path:
        checkpoint_directory = self.directory.joinpath(image.name)
        checkpoint_directory.mkdir(exist_ok=True)
        checkpoint = checkpoint_directory.joinpath(name).with_suffix(".png")
        return checkpoint

    def post(
        self, name: str
    ) -> Callable[[Callable[[PipeImage], PipeImage]], Callable[[PipeImage], PipeImage]]:
        if name in self.checkpoint_names:
            raise ValueError
        self.checkpoint_names.add(name)

        def checkpoint_decorator(
            function: Callable[[PipeImage], PipeImage]
        ) -> Callable[[PipeImage], PipeImage]:
            @wraps(function)
            def wrapped(image: PipeImage) -> PipeImage:
                self.image_names.add(image.name)
                checkpoint = self.get_checkpoint(image, name)
                if checkpoint.exists():
                    output_image = PipeImage(path=checkpoint, parents=image)
                    info(f"{self}: {image.name} checkpoint {checkpoint.name} loaded")
                else:
                    output_image = function(image)
                    output_image.image.save(checkpoint)
                    info(f"{self}: {image.name} checkpoint {checkpoint.name} saved")
                return output_image

            return wrapped

        return checkpoint_decorator

    def pre(
        self, name: str
    ) -> Callable[[Callable[[PipeImage], PipeImage]], Callable[[PipeImage], PipeImage]]:
        def checkpoint_decorator(
            function: Callable[[PipeImage], PipeImage]
        ) -> Callable[[PipeImage], PipeImage]:
            if name in self.checkpoint_names:
                raise ValueError
            self.checkpoint_names.add(name)

            @wraps(function)
            def wrapped(image: PipeImage) -> PipeImage:
                self.image_names.add(image.name)
                checkpoint = self.get_checkpoint(image, name)
                if not checkpoint.exists():
                    image.image.save(checkpoint)
                    info(f"{self}: {image.name} checkpoint {checkpoint.name} saved")
                return function(image)

            return wrapped

        return checkpoint_decorator

    def purge_unrecognized_files(self) -> None:
        for checkpoint_directory in self.directory.iterdir():
            for checkpoint in checkpoint_directory.iterdir():
                if (
                    checkpoint.is_file()
                    and checkpoint.parts[-1] not in self.image_names
                    and checkpoint.stem not in self.checkpoint_names
                ):
                    remove(checkpoint)
                    info(
                        f"{self}: checkpoint "
                        f"{join(checkpoint.parts[-1],checkpoint.name)} removed"
                    )
            if not any(checkpoint_directory.iterdir()):
                remove(checkpoint_directory)
                info(
                    f"{self}: checkpoint directory {checkpoint_directory.parts[-1]} "
                    f"removed"
                )
