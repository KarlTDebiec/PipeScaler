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
from typing import Callable, Collection, Optional

from pipescaler.common import get_temp_file_path
from pipescaler.core.pipelines import (
    CheckpointManagerBase,
    PipeImage,
    PipeWithPreCheckpoints,
)
from pipescaler.core.pipelines.pipe_stage import PipeStage
from pipescaler.core.pipelines.pipe_with_post_checkpoints import PipeWithPostCheckpoints


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

    def post(
        self, *cpts: str, calls: Optional[Collection[PipeStage]] = None
    ) -> Callable[[PipeStage], PipeWithPostCheckpoints]:
        internal_cpts = self.get_internal_cpts(*calls) if calls else []

        def decorator(stage: PipeStage) -> PipeWithPostCheckpoints:
            internal_cpts.extend(self.get_internal_cpts(stage))

            return PipeWithPostCheckpoints(stage, self, cpts, internal_cpts)

        return decorator

    def pre(
        self, *cpts: str, calls: Optional[Collection[PipeStage]] = None
    ) -> Callable[[PipeStage], PipeWithPreCheckpoints]:
        internal_cpts = self.get_internal_cpts(*calls) if calls else []

        def decorator(stage: PipeStage) -> PipeWithPreCheckpoints:
            internal_cpts.extend(self.get_internal_cpts(stage))

            return PipeWithPreCheckpoints(stage, self, cpts, internal_cpts)

        return decorator

    def purge_unrecognized_files(self) -> None:
        """Remove files in output directory that have not been logged as observed."""
        for img in self.directory.iterdir():
            if img.is_dir():
                for cpt in img.iterdir():
                    if cpt.is_dir():
                        rmdir(cpt)
                        info(f"{self}: directory {join(img.name, cpt.name)} removed")
                    elif (img.name, cpt.name) not in self.observed_checkpoints:
                        remove(cpt)
                        info(f"{self}: file {join(img.name, cpt.name)} removed")
                if not any(img.iterdir()):
                    rmdir(img)
                    info(f"{self}: directory {img.name} removed")
            else:
                remove(img)
                info(f"{self}: file {img.name} removed")

    @staticmethod
    def get_internal_cpts(*called_functions: PipeStage) -> list[str]:
        internal_cpts: list[str] = []
        for function in called_functions:
            if hasattr(function, "cpt"):
                internal_cpts.append(getattr(function, "cpt"))
            if hasattr(function, "cpts"):
                internal_cpts.extend(getattr(function, "cpts"))
            if hasattr(function, "internal_cpts"):
                internal_cpts.extend(getattr(function, "internal_cpts"))
        return internal_cpts
