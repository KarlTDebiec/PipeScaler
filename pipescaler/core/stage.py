#!/usr/bin/env python
#   pipescaler/core/stage.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generator, Optional

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
        self._pipeline = pipeline
        if name is not None:
            self._name = name
        if desc is not None:
            self._desc = desc

    @abstractmethod
    def __call__(self) -> Generator[str, str, None]:
        raise NotImplementedError()

    def __repr__(self) -> str:
        return self.desc

    def __str__(self) -> str:
        return self.name

    # endregion

    # region Properties

    @property
    def desc(self) -> str:
        """str: Description"""
        if not hasattr(self, "_desc"):
            self._desc = self.name
        return self._desc

    @property
    def name(self) -> str:
        """str: Name"""
        if not hasattr(self, "_name"):
            self._name = self.__class__.__name__
        return self._name

    @property
    def pipeline(self) -> Pipeline:
        """Pipeline: Pipeline"""
        return self._pipeline

    # endregion
