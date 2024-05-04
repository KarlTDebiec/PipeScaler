#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for image termini."""
from __future__ import annotations

from abc import ABC, abstractmethod

from pipescaler.core.pipelines.terminus import Terminus
from pipescaler.image.core.pipelines.pipe_image import PipeImage


class ImageTerminus(Terminus, ABC):
    """Abstract base class for image termini."""

    @abstractmethod
    def __call__(self, input_image: PipeImage) -> None:
        """Terminates image."""
        raise NotImplementedError
