#!/usr/bin/env python
#   pipescaler/core/stage.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generator, Optional

from pipescaler.core.pipe_image import PipeImage
from pipescaler.core.pipeline import Pipeline


####################################### CLASSES ########################################
class Stage(ABC):

    # region Builtins

    def __init__(
        self,
        pipeline: Pipeline,
        name: Optional[str] = None,
        desc: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        self.pipeline = pipeline
        if name is not None:
            self.name = name
        else:
            self.name = self.__class__.__name__
        if desc is not None:
            self.desc = desc
        else:
            self.desc = self.name

    @abstractmethod
    def __call__(self) -> Generator[PipeImage, PipeImage, None]:
        raise NotImplementedError()

    def __repr__(self) -> str:
        return self.desc

    def __str__(self) -> str:
        return self.name

    # endregion
