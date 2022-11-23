#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for checkpoint managers."""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union

from pipescaler.common import validate_output_directory
from pipescaler.core.pipelines.pipe_image import PipeImage


class CheckpointManagerBase(ABC):
    """Abstract base class for checkpoint managers."""

    def __init__(self, directory: Union[Path, str]) -> None:
        """Validate and store configuration.

        Arguments:
            directory: Directory in which to store checkpoints
        """
        self.directory = validate_output_directory(directory)
        """Directory in which to store checkpoints."""
        self.observed_checkpoints: set[tuple[str, str]] = set()
        """Observed checkpoints as tuples of image and checkpoint names."""

    @abstractmethod
    def observe(self, img: PipeImage, cpt: str) -> None:
        """Observe an image."""
        raise NotImplementedError()
