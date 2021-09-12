#!/usr/bin/env python
#   pipescaler/core/merger.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
""""""
from __future__ import annotations

from abc import ABC
from typing import Any, Dict, Optional

from pipescaler.core.stage import Stage


class Merger(Stage, ABC):
    def __init__(
        self,
        suffix: Optional[str] = None,
        trim_suffixes: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)

        # Store configuration
        if suffix is not None:
            self.suffix = suffix
        else:
            self.suffix = "merge"
        if trim_suffixes is not None:
            self.trim_suffixes = trim_suffixes
        else:
            self.trim_suffixes = self.inlets

    def __call__(self, outfile: str) -> None:
        raise NotImplementedError()

    @property
    def outlets(self):
        return ["outlet"]
