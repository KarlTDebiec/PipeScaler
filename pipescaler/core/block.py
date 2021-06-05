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

from typing import Any

from pipescaler.core import Stage

####################################### CLASSES ########################################
class Block(Stage):

    # region Builtins

    def __init__(self, stages, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        # Store configuration
        self.stages = stages

    # endregion

    # region Properties

    @property
    def inlets(self):
        return self.stages[0].inlets

    @property
    def outlets(self):
        return self.stages[-1].outlets

    # endregion
