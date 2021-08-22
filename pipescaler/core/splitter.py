#!/usr/bin/env python
#   pipescaler/core/splitter.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from abc import ABC
from typing import Any, Dict, Optional

from pipescaler.core.stage import Stage


####################################### CLASSES ########################################
class Splitter(Stage, ABC):

    # region Builtins

    def __init__(
        self, suffixes: Optional[Dict[str, str]] = None, **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)

        # Store configuration
        if suffixes is not None:
            self.suffixes = suffixes
        else:
            self.suffixes = {outlet: outlet for outlet in self.outlets}

    def __call__(self, infile: str, **kwargs: Any) -> Dict[str, str]:
        raise NotImplementedError()

    # endregion

    # region Properties

    @property
    def inlets(self):
        return ["infile"]

    # endregion
