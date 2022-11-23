#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Manages checkpoints."""
from functools import wraps
from logging import info
from os import remove, rmdir
from os.path import join
from pathlib import Path
from typing import Callable, Collection, Optional, Union

from pipescaler.common import get_temp_file_path
from pipescaler.core.pipelines import (
    CheckpointManagerBase,
    PipeImage,
    PipeProcessorWithCheckpoints,
    PipeProcessorWithPostCheckpoint,
    PipeProcessorWithPreCheckpoint,
    PipeSplitterWithPostCheckpoints,
)


class CheckpointManager(CheckpointManagerBase):
    """Manages checkpoints."""

    def __repr__(self):
        """Representation."""
        return f"{self.__class__.__name__}(directory={self.directory})"

    def post_file_processor(
        self, cpt: str
    ) -> Callable[[Callable[[Path, Path], None]], Callable[[PipeImage], PipeImage]]:
        """Get a decorator to be used to add a checkpoint after a processor function.

        Arguments:
            cpt: Name of checkpoint
        Returns:
            Decorator to be used to add checkpoint after a PipeFileProcessor function
        """

        def decorator(
            function: Callable[[Path, Path], None]
        ) -> Callable[[PipeImage], PipeImage]:
            """Decorator to be used to add a checkpoint after a processor function.

            Arguments:
                function: Function to wrap
            Returns:
                Wrapped function
            """

            @wraps(function)
            def wrapped(input_img: PipeImage) -> PipeImage:
                """Image processor function, wrapped to make use of a checkpoint.

                Arguments:
                    input_img: Image to process
                Returns:
                    Processed image, loaded from checkpoint if available
                """
                self.observed_checkpoints.add((input_img.name, cpt))

                cpt_path = self.directory / input_img.name / cpt
                if cpt_path.exists():
                    output_img = PipeImage(path=cpt_path, parents=input_img)
                    info(f"{self}: {input_img.name} checkpoint {cpt} loaded")
                else:
                    if not cpt_path.parent.exists():
                        cpt_path.parent.mkdir(parents=True)
                    if input_img.path is None:
                        with get_temp_file_path(".png") as input_path:
                            input_img.image.save(input_path)
                            function(input_path, cpt_path)
                    else:
                        function(input_img.path, cpt_path)
                    output_img = PipeImage(path=cpt_path, parents=input_img)
                    info(f"{self}: {input_img.name} checkpoint {cpt} saved")

                return output_img

            return wrapped

        return decorator

    def post_processor(
        self,
        cpt: str,
        *called_functions: Callable[[PipeImage], PipeImage],
    ) -> Callable[[Callable[[PipeImage], PipeImage]], PipeProcessorWithCheckpoints]:
        """Get a decorator to be used to add a checkpoint after a processor function.

        Arguments:
            cpt: Name of checkpoints
            called_functions: Functions called by the wrapped function
        Returns:
            Decorator to be used to add checkpoint after a PipeProcessor
        """
        internal_cpts: list[str] = []
        for function in called_functions:
            if isinstance(function, PipeProcessorWithCheckpoints):
                internal_cpts.append(function.cpt)
                internal_cpts.extend(function.internal_cpts)

        def decorator(
            function: Callable[[PipeImage], PipeImage]
        ) -> PipeProcessorWithCheckpoints:
            """Decorator to be used to add a checkpoint after a processor function.

            Arguments:
                function: Function to wrap
            Returns:
                Wrapped function
            """

            @wraps(function)
            def wrapped(input_img: PipeImage) -> PipeImage:
                """Image processor function, wrapped to make use of a checkpoint.

                Arguments:
                    input_img: Image to process
                Returns:
                    Processed image, loaded from checkpoint if available
                """
                self.observed_checkpoints.add((input_img.name, cpt))
                self.observed_checkpoints.update(
                    [(input_img.name, internal_cpt) for internal_cpt in internal_cpts]
                )

                cpt_path = self.directory / input_img.name / cpt
                if cpt_path.exists():
                    output_img = PipeImage(path=cpt_path, parents=input_img)
                    info(f"{self}: {input_img.name} checkpoint {cpt} loaded")
                else:
                    output_img = function(input_img)
                    if not cpt_path.parent.exists():
                        cpt_path.parent.mkdir(parents=True)
                    output_img.save(cpt_path)
                    info(f"{self}: {input_img.name} checkpoint {cpt} saved")
                return output_img

            if isinstance(function, PipeProcessorWithCheckpoints):
                internal_cpts.append(function.cpt)
                internal_cpts.extend(function.internal_cpts)

            return PipeProcessorWithCheckpoints(wrapped, cpt, internal_cpts)

        return decorator

    def post_splitter(
        self, *cpts: str
    ) -> Callable[
        [Callable[[PipeImage], tuple[PipeImage, ...]]],
        Callable[[PipeImage], tuple[PipeImage, ...]],
    ]:
        """Get a decorator to be used to add checkpoints after a splitter function.

        Arguments:
            cpts: Names of checkpoints
        Returns:
            Decorator to be used to add checkpoints after a PipeSplitter
        """

        def decorator(
            function: Callable[[PipeImage], tuple[PipeImage, ...]]
        ) -> Callable[[PipeImage], tuple[PipeImage, ...]]:
            """Decorator to be used to add a checkpoint after a processor function.

            Arguments:
                function: Function to wrap
            Returns:
                Wrapped function
            """

            @wraps(function)
            def wrapped(input_img: PipeImage) -> tuple[PipeImage, ...]:
                """Image splitter function, wrapped to make use of checkpoints.

                Arguments:
                    input_img: Image to split
                Returns:
                    Split images, loaded from checkpoint if available
                """
                self.observed_checkpoints.update((input_img.name, cpt) for cpt in cpts)

                cpt_paths = [self.directory / input_img.name / cpt for cpt in cpts]
                if all(cpt_path.exists() for cpt_path in cpt_paths):
                    output_imgs = tuple(
                        PipeImage(path=cpt_path, parents=input_img)
                        for cpt_path in cpt_paths
                    )
                    info(f"{self}: {input_img.name} checkpoints {cpts} loaded")
                else:
                    output_imgs = function(input_img)
                    if not cpt_paths[0].parent.exists():
                        cpt_paths[0].parent.mkdir(parents=True)
                    for output_img, cpt_path in zip(output_imgs, cpt_paths):
                        output_img.save(cpt_path)
                        info(f"{self}: {input_img.name} checkpoint {cpt_path} saved")
                return output_imgs

            return wrapped

        return decorator

    def pre_processor(
        self,
        cpt: str,
        *called_functions: Callable[[PipeImage], PipeImage],
    ) -> Callable[[Callable[[PipeImage], PipeImage]], PipeProcessorWithCheckpoints]:
        """Get a decorator to be used to add a checkpoint before a processor function.

        Arguments:
            cpt: Name of checkpoint
            called_functions: Functions called by the wrapped function
        Returns:
            Decorator to be used to add checkpoint before a processor function.
        """
        internal_cpts: list[str] = []
        for function in called_functions:
            if isinstance(function, PipeProcessorWithCheckpoints):
                internal_cpts.append(function.cpt)
                internal_cpts.extend(function.internal_cpts)

        def decorator(
            function: Callable[[PipeImage], PipeImage]
        ) -> PipeProcessorWithCheckpoints:
            """Decorator to be used to add a checkpoint before a processor function.

            Arguments:
                function: Function to wrap
            Returns:
                Wrapped function
            """

            @wraps(function)
            def wrapped(input_img: PipeImage) -> PipeImage:
                """Image processor function, wrapped to make use of a checkpoint.

                Arguments:
                    input_img: Image to process
                Returns:
                    Processed image, loaded from checkpoint if available
                """
                self.observed_checkpoints.add((input_img.name, cpt))
                self.observed_checkpoints.update(
                    [(input_img.name, internal_cpt) for internal_cpt in internal_cpts]
                )

                cpt_path = self.directory / input_img.name / cpt
                if not cpt_path.exists():
                    input_img.save(cpt_path)
                    info(f"{self}: {input_img.name} checkpoint {cpt} saved")
                return function(input_img)

            if isinstance(function, PipeProcessorWithCheckpoints):
                internal_cpts.append(function.cpt)
                internal_cpts.extend(function.internal_cpts)

            return PipeProcessorWithCheckpoints(wrapped, cpt, internal_cpts)

        return decorator

    def observe(self, img: PipeImage, cpt: str) -> None:
        self.observed_checkpoints.add((img.name, cpt))

    def post_processor2(
        self,
        cpt: str,
        *,
        calls: Optional[Collection[Callable[[PipeImage], PipeImage]]] = None,
    ) -> Callable[[Callable[[PipeImage], PipeImage]], PipeProcessorWithPostCheckpoint]:
        internal_cpts = self.get_internal_cpts(*calls) if calls else []

        def decorator(
            processor: Callable[[PipeImage], PipeImage]
        ) -> PipeProcessorWithPostCheckpoint:
            internal_cpts.extend(self.get_internal_cpts(processor))

            return PipeProcessorWithPostCheckpoint(processor, self, cpt, internal_cpts)

        return decorator

    def pre_processor2(
        self,
        cpt: str,
        *,
        calls: Optional[Collection[Callable[[PipeImage], PipeImage]]] = None,
    ) -> Callable[[Callable[[PipeImage], PipeImage]], PipeProcessorWithPreCheckpoint]:
        internal_cpts = self.get_internal_cpts(*calls) if calls else []

        def decorator(
            processor: Callable[[PipeImage], PipeImage]
        ) -> PipeProcessorWithPreCheckpoint:
            internal_cpts.extend(self.get_internal_cpts(processor))

            return PipeProcessorWithPreCheckpoint(processor, self, cpt, internal_cpts)

        return decorator

    def post_splitter2(
        self,
        *cpts: str,
        calls: Optional[Collection[Callable[[PipeImage], PipeImage]]] = None,
    ) -> Callable[
        [Callable[[PipeImage], tuple[PipeImage, ...]]],
        PipeSplitterWithPostCheckpoints,
    ]:
        internal_cpts = self.get_internal_cpts(*calls) if calls else []

        def decorator(
            splitter: Callable[[PipeImage], tuple[PipeImage, ...]]
        ) -> PipeSplitterWithPostCheckpoints:
            internal_cpts.extend(self.get_internal_cpts(splitter))

            return PipeSplitterWithPostCheckpoints(splitter, self, cpts, internal_cpts)

        return decorator

    def purge_unrecognized_files(self) -> None:
        """Remove files in output directory that have not been logged as observed."""
        for img in self.directory.iterdir():
            for cpt in img.iterdir():
                if (img.name, cpt.name) not in self.observed_checkpoints:
                    name = join(cpt.parents[0].name, cpt.name)
                    if cpt.is_dir():
                        rmdir(cpt)
                    else:
                        remove(cpt)
                    info(f"{self}: checkpoint {name} removed")
            if not any(img.iterdir()):
                rmdir(img)
                info(f"{self}: directory {img.name} removed")

    @staticmethod
    def get_internal_cpts(
        *called_functions: Union[
            Callable[[PipeImage], PipeImage],
            Callable[[PipeImage], tuple[PipeImage, ...]],
        ],
    ) -> list[str]:
        internal_cpts: list[str] = []
        for function in called_functions:
            if hasattr(function, "cpt"):
                internal_cpts.append(getattr(function, "cpt"))
            if hasattr(function, "cpts"):
                internal_cpts.extend(getattr(function, "cpts"))
            if hasattr(function, "internal_cpts"):
                internal_cpts.extend(getattr(function, "internal_cpts"))
        return internal_cpts
