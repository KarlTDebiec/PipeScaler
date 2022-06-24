#!/usr/bin/env python
#  Copyright (C) 2020-2022. Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Manages checkpoints."""
from functools import wraps
from logging import info
from os import remove, rmdir
from os.path import join
from pathlib import Path
from typing import Callable, Optional, Sequence, Union

from pipescaler.common import temporary_filename, validate_output_directory
from pipescaler.core.pipelines import PipeImage


class CheckpointManager:
    """Manages checkpoints."""

    def __init__(self, directory: Union[Path, str]) -> None:
        """Validate and store configuration.

        Arguments:
            directory: Directory in which to store checkpoints
        """
        self.directory = Path(
            validate_output_directory(directory, create_directory=True)
        )
        self.image_names = set()
        self.checkpoint_names = set()

    def __repr__(self):
        """Representation."""
        return f"<{self.__class__.__name__}>"

    def get_checkpoint(
        self, image: PipeImage, name: str, suffix: Optional[str] = ".png"
    ) -> Path:
        """Get the path to a checkpoint for a provided image and name.

        Argumentss:
            image: Image; used to determine subfolder
            name: Name of checkpoint
            suffix: Suffix of checkpoint
        Returns:
            Path to checkpoint
        """
        checkpoint_directory = self.directory.joinpath(image.name)
        if not checkpoint_directory.exists():
            checkpoint_directory.mkdir()
        checkpoint = checkpoint_directory.joinpath(name).with_suffix(suffix)
        return checkpoint

    def post(
        self, name: str
    ) -> Callable[[Callable[[PipeImage], PipeImage]], Callable[[PipeImage], PipeImage]]:
        """Get a decorator to be used to add a checkpoint after a processor function.

        Arguments:
            name: Name of checkpoint
        Returns:
            Decorator to be used to add checkpoint after a processor function
        """
        self.checkpoint_names.add(name)

        def checkpoint_decorator(
            function: Callable[[PipeImage], PipeImage]
        ) -> Callable[[PipeImage], PipeImage]:
            """Decorator to be used to add a checkpoint after a processor function.

            Arguments:
                function: Function to wrap
            Returns:
                Wrapped function
            """

            @wraps(function)
            def wrapped(image: PipeImage) -> PipeImage:
                """Image processor function, wrapped to make use of a checkpoint.

                Arguments:
                    image: Image to process
                Returns:
                    Processed image, loaded from checkpoint if available
                """
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

    def post_file(
        self, name: str, suffix: Optional[str] = ".png"
    ) -> Callable[[Callable[[Path, Path], None]], Callable[[PipeImage], PipeImage]]:
        """Get a decorator to be used to add a checkpoint after a processor function.

        Arguments:
            name: Name of checkpoint
            suffix: Suffix of checkpoint
        Returns:
            Decorator to be used to add checkpoint after a processor function
        """
        self.checkpoint_names.add(name)

        def checkpoint_decorator(
            function: Callable[[Path, Path], None]
        ) -> Callable[[PipeImage], PipeImage]:
            """Decorator to be used to add a checkpoint after a processor function.

            Arguments:
                function: Function to wrap
            Returns:
                Wrapped function
            """

            @wraps(function)
            def wrapped(image: PipeImage) -> PipeImage:
                """Image processor function, wrapped to make use of a checkpoint.

                Arguments:
                    image: Image to process
                Returns:
                    Processed image, loaded from checkpoint if available
                """
                self.image_names.add(image.name)
                checkpoint = self.get_checkpoint(image, name, suffix=suffix)
                if checkpoint.exists():
                    output_image = PipeImage(path=checkpoint, parents=image)
                    info(f"{self}: {image.name} checkpoint {checkpoint.name} loaded")
                else:
                    if image.path is None:
                        with temporary_filename(".png") as infile:
                            infile = Path(infile)
                            image.image.save(infile)
                            function(infile, checkpoint)
                    else:
                        function(image.path, checkpoint)
                    output_image = PipeImage(path=checkpoint, parents=image)
                    info(f"{self}: {image.name} checkpoint {checkpoint.name} saved")
                return output_image

            return wrapped

        return checkpoint_decorator

    def post_splitter(
        self, names: Sequence[str]
    ) -> Callable[
        [Callable[[PipeImage], tuple[PipeImage, ...]]],
        Callable[[PipeImage], tuple[PipeImage, ...]],
    ]:
        """Get a decorator to be used to add checkpoints after a splitter function.

        Arguments:
            names: Names of checkpoints
        Returns:
            Decorator to be used to add checkpoints after a splitter function
        """
        self.checkpoint_names.add(names)

        def checkpoint_decorator(
            function: Callable[[PipeImage], tuple[PipeImage, ...]]
        ) -> Callable[[PipeImage], tuple[PipeImage, ...]]:
            """Decorator to be used to add a checkpoint after a processor function.

            Arguments:
                function: Function to wrap
            Returns:
                Wrapped function
            """

            @wraps(function)
            def wrapped(image: PipeImage) -> tuple[PipeImage, ...]:
                """Image splitter function, wrapped to make use of checkpoints.

                Arguments:
                    image: Image to split
                Returns:
                    Split images, loaded from checkpoint if available
                """
                self.image_names.add(image.name)
                checkpoints = [self.get_checkpoint(image, name) for name in names]
                if all(checkpoint.exists() for checkpoint in checkpoints):
                    output_images = tuple(
                        PipeImage(path=checkpoint, parents=image)
                        for checkpoint in checkpoints
                    )
                    info(f"{self}: {image.name} checkpoints {names} loaded")
                else:
                    output_images = function(image)
                    for output_image, checkpoint in zip(output_images, checkpoints):
                        output_image.image.save(checkpoint)
                        info(f"{self}: {image.name} checkpoint {checkpoint.name} saved")
                return output_images

            return wrapped

        return checkpoint_decorator

    def pre(
        self, name: str
    ) -> Callable[[Callable[[PipeImage], PipeImage]], Callable[[PipeImage], PipeImage]]:
        """Get a decorator to be used to add a checkpoint before a processor function.

        Arguments:
            name: Name of checkpoint
        Returns:
            Decorator to bue used to add checkpoint before a processor function.
        """

        def checkpoint_decorator(
            function: Callable[[PipeImage], PipeImage]
        ) -> Callable[[PipeImage], PipeImage]:
            """Decorator to be used to add a checkpoint before a processor function.

            Arguments:
                function: Function to wrap
            Returns:
                Wrapped function
            """
            self.checkpoint_names.add(name)

            @wraps(function)
            def wrapped(image: PipeImage) -> PipeImage:
                """Image processor function, wrapped to make use of a checkpoint.

                Arguments:
                    image: Image to process
                Returns:
                    Processed image, loaded from checkpoint if available
                """
                self.image_names.add(image.name)
                checkpoint = self.get_checkpoint(image, name)
                if not checkpoint.exists():
                    image.image.save(checkpoint)
                    info(f"{self}: {image.name} checkpoint {checkpoint.name} saved")
                return function(image)

            return wrapped

        return checkpoint_decorator

    def purge_unrecognized_files(self) -> None:
        """Remove files in output directory that have not been logged as observed."""
        for checkpoint_directory in self.directory.iterdir():
            for checkpoint in checkpoint_directory.iterdir():
                if (
                    checkpoint_directory.name not in self.image_names
                    or checkpoint.stem not in self.checkpoint_names
                ):
                    remove(checkpoint)
                    info(
                        f"{self}: checkpoint "
                        f"{join(checkpoint_directory.name,checkpoint.name)} removed"
                    )
            if checkpoint_directory.name not in self.image_names or not any(
                checkpoint_directory.iterdir()
            ):
                rmdir(checkpoint_directory)
                info(
                    f"{self}: checkpoint directory "
                    f"{checkpoint_directory.name} removed"
                )
