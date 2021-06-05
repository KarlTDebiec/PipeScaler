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
from typing import Any, Optional


####################################### CLASSES ########################################
class Stage(ABC):

    # region Builtins

    def __init__(
        self, name: Optional[str] = None, desc: Optional[str] = None, **kwargs: Any
    ) -> None:
        if name is not None:
            self.name = name
        else:
            self.name = self.__class__.__name__
        if desc is not None:
            self.desc = desc
        else:
            self.desc = self.name

    def __repr__(self) -> str:
        return self.desc

    def __str__(self) -> str:
        return self.name

    # endregion

    # region Properties

    @property
    @abstractmethod
    def inlets(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def outlets(self):
        raise NotImplementedError()

    # endregion
