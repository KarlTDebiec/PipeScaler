#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Checkpoint manager."""
from itertools import tee
from logging import info
from os import remove
from pathlib import Path
from typing import Iterator

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
        self.names = set()
        self.observed_files = set()

    def cp(self, name: str, inlet: Iterator[PipeImage]):
        if name in self.names:
            raise ValueError()
        self.names.add(name)
        return Checkpoint(self, name, inlet)

    def purge_unrecognized_files(self) -> None:
        for checkpoint_directory in self.directory.iterdir():
            for checkpoint in checkpoint_directory.iterdir():
                if checkpoint.is_file() and checkpoint not in self.observed_files:
                    remove(checkpoint)
                    info(f"{self}: '{checkpoint}' removed")
            if not any(checkpoint_directory.iterdir()):
                remove(checkpoint_directory)
                info(f"{self}: '{checkpoint_directory}' removed")


class Checkpoint:
    def __init__(
        self, manager: CheckpointManager, name: str, inlet: Iterator[PipeImage]
    ) -> None:
        """Validate and store configuration.

        Arguments:
            directory: Directory to which to copy images
        """
        self.manager = manager
        self.name = name
        self.inlet = inlet

    def __enter__(self):
        def iterator() -> Iterator[tuple[bool, PipeImage]]:
            for pipe_image in self.inlet:
                checkpoint_directory = self.directory.joinpath(pipe_image.name)
                checkpoint_directory.mkdir(exist_ok=True)
                checkpoint = checkpoint_directory.joinpath(self.name).with_suffix(
                    ".png"
                )
                if checkpoint.exists():
                    print(f"{self}: '{checkpoint}' exists")
                    self.manager.observed_files.add(checkpoint)
                    yield (True, pipe_image)
                else:
                    print(f"{self}: '{checkpoint}' does not exist")
                    yield (False, pipe_image)

        tees = tee(iterator())
        self.done = (elem[1] for elem in tees[0] if elem[0])
        self.to_do = (elem[1] for elem in tees[1] if not elem[0])

        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        pass

    def save(self, unavailable: Iterator[PipeImage]) -> Iterator[PipeImage]:
        def iterator() -> Iterator[PipeImage]:
            for pipe_image in self.done:
                checkpoint_directory = self.directory.joinpath(pipe_image.name)
                checkpoint = checkpoint_directory.joinpath(self.name).with_suffix(
                    ".png"
                )
                print(f"{self}: '{checkpoint}' used")
                yield PipeImage(path=checkpoint, parents=pipe_image)
            for pipe_image in unavailable:
                checkpoint_directory = self.directory.joinpath(pipe_image.name)
                checkpoint = checkpoint_directory.joinpath(self.name).with_suffix(
                    ".png"
                )
                pipe_image.image.save(checkpoint)
                print(f"{self}: '{checkpoint}' saved")
                self.manager.observed_files.add(checkpoint)
                yield pipe_image

        return iterator()

    @property
    def directory(self):
        return self.manager.directory
