#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Manages checkpoints."""
from functools import wraps
from logging import info
from os import remove
from os.path import join
from pathlib import Path
from typing import Callable, Sequence, Union

from pipescaler.common import get_temp_file_path, validate_output_directory
from pipescaler.core.pipelines import PipeImage
from pipescaler.core.typing import PipeFileProcessor, PipeProcessor, PipeSplitter


class CheckpointManager:
    """Manages checkpoints."""

    def __init__(self, directory: Union[Path, str]) -> None:
        """Validate and store configuration.

        Attributes:
            directory: Directory in which to store checkpoints
            image_names: Names of images for which checkpoints have been created
            checkpoint_names: Names of checkpoints

        Arguments:
            directory: Directory in which to store checkpoints
        """
        self.directory = validate_output_directory(directory)
        """Directory in which to store checkpoints."""
        self.observed_checkpoints: set[tuple[str, str]] = set()
        """Observed checkpoints as tuples of image and checkpoint names."""

    def __repr__(self):
        """Representation."""
        return f"<{self.__class__.__name__}>"

    def post_processor(
        self,
        checkpoint_name: str,
    ) -> Callable[[PipeProcessor], PipeProcessor]:
        """Get a decorator to be used to add a checkpoint after a processor function.

        Arguments:
            checkpoint_name: Name of checkpoints
        Returns:
            Decorator to be used to add checkpoint after a processor function
        """
        # self.checkpoint_names.add(checkpoint_name)

        def decorator(function: PipeProcessor) -> PipeProcessor:
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
                self.observed_checkpoints.add((image.name, checkpoint_name))

                checkpoint_path = self.directory / image.name / checkpoint_name
                if checkpoint_path.exists():
                    output_image = PipeImage(path=checkpoint_path, parents=image)
                    info(f"{self}: {image.name} checkpoint {checkpoint_name} loaded")
                else:
                    output_image = function(image)
                    output_image.image.save(checkpoint_path)
                    info(f"{self}: {image.name} checkpoint {checkpoint_name} saved")
                return output_image

            return wrapped

        return decorator

    def post_file_processor(
        self, checkpoint_name: str
    ) -> Callable[[PipeFileProcessor], PipeProcessor]:
        """Get a decorator to be used to add a checkpoint after a processor function.

        Arguments:
            checkpoint_name: Name of checkpoint
            suffix: Suffix of checkpoint
        Returns:
            Decorator to be used to add checkpoint after a processor function
        """

        def decorator(function: PipeFileProcessor) -> PipeProcessor:
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
                self.observed_checkpoints.add((image.name, checkpoint_name))

                checkpoint_path = self.directory / image.name / checkpoint_name
                if checkpoint_path.exists():
                    output_image = PipeImage(path=checkpoint_path, parents=image)
                    info(f"{self}: {image.name} checkpoint {checkpoint_name} loaded")
                else:
                    if image.path is None:
                        with get_temp_file_path(".png") as input_path:
                            image.image.save(input_path)
                            function(input_path, checkpoint_path)
                    else:
                        function(image.path, checkpoint_path)
                    output_image = PipeImage(path=checkpoint_path, parents=image)
                    info(f"{self}: {image.name} checkpoint {checkpoint_name} saved")
                return output_image

            return wrapped

        return decorator

    def post_splitter(
        self, checkpoint_names: Sequence[str]
    ) -> Callable[[PipeSplitter], PipeSplitter]:
        """Get a decorator to be used to add checkpoints after a splitter function.

        Arguments:
            checkpoint_names: Names of checkpoints
        Returns:
            Decorator to be used to add checkpoints after a splitter function
        """

        def decorator(function: PipeSplitter) -> PipeSplitter:
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
                self.observed_checkpoints.update(
                    (image.name, checkpoint_name)
                    for checkpoint_name in checkpoint_names
                )

                checkpoint_paths = [
                    self.directory / image.name / checkpoint_name
                    for checkpoint_name in checkpoint_names
                ]
                if all(cp.exists() for cp in checkpoint_paths):
                    output_images = tuple(
                        PipeImage(path=cp, parents=image) for cp in checkpoint_paths
                    )
                    info(f"{self}: {image.name} checkpoints {checkpoint_names} loaded")
                else:
                    output_images = function(image)
                    for output_image, cp in zip(output_images, checkpoint_paths):
                        output_image.image.save(cp)
                        info(f"{self}: {image.name} checkpoint {cp} saved")
                return output_images

            return wrapped

        return decorator

    def pre_processor(
        self, checkpoint_name: str
    ) -> Callable[[PipeProcessor], PipeProcessor]:
        """Get a decorator to be used to add a checkpoint before a processor function.

        Arguments:
            checkpoint_name: Name of checkpoint
        Returns:
            Decorator to bue used to add checkpoint before a processor function.
        """

        def decorator(function: PipeProcessor) -> PipeProcessor:
            """Decorator to be used to add a checkpoint before a processor function.

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
                self.observed_checkpoints.add((image.name, checkpoint_name))

                checkpoint_path = self.directory / image.name / checkpoint_name
                if not checkpoint_path.exists():
                    image.image.save(checkpoint_path)
                    info(f"{self}: {image.name} checkpoint {checkpoint_path} saved")
                return function(image)

            return wrapped

        return decorator

    def purge_unrecognized_files(self) -> None:
        """Remove files in output directory that have not been logged as observed."""
        for image_directory in self.directory.iterdir():
            for checkpoint in image_directory.iterdir():
                if (
                    image_directory.name,
                    checkpoint.name,
                ) not in self.observed_checkpoints:
                    remove(checkpoint)
                    info(
                        f"{self}: checkpoint "
                        f"{join(checkpoint.parents[0].name, checkpoint.name)} removed"
                    )
            if not any(image_directory.iterdir()):
                remove(image_directory)
                info(f"{self}: directory {image_directory.name} removed")
