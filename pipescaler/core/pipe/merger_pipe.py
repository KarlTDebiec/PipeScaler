#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for merger pipes."""
from abc import ABC, abstractmethod
from typing import Any, Optional, Type

from pipescaler.core import PipeImage
from pipescaler.core.pipe.pipe import Pipe
from pipescaler.core.stages import Merger


class MergerPipe(Pipe, ABC):
    def __init__(
        self,
        suffix: Optional[str] = None,
        trim_suffixes: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            suffix: Suffix to add to merged outfiles
            trim_suffixes: Suffixes to trim from merged outfiles
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Store configuration
        self.suffix = suffix if suffix is not None else "merge"
        self.trim_suffixes = trim_suffixes if trim_suffixes is not None else self.inlets

        self.merger_object = self.merger(**kwargs)

    def __call__(self, inlets: dict[str, PipeImage]) -> dict[str, PipeImage]:
        inlet_images = [inlets[inlet].image for inlet in inlets]
        outlet_image = self.merger_object(*inlet_images)
        return {"outlet": PipeImage(outlet_image, list(inlets.values()))}

    @property
    def outlets(self) -> list[str]:
        """Outlets that flow out of pipe."""
        return ["outlet"]

    @classmethod
    @property
    @abstractmethod
    def merger(cls) -> Type[Merger]:
        """Type of merger wrapped by pipe."""
        raise NotImplementedError()
