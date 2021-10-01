#!/usr/bin/env python
#   pipescaler/core/merger.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List, Optional

from pipescaler.core.stage import Stage


class Merger(Stage, ABC):
    def __init__(
        self,
        suffix: Optional[str] = None,
        trim_suffixes: Optional[List[str]] = None,
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

    @abstractmethod
    def __call__(self, outfile: str, **kwargs: Any) -> None:
        raise NotImplementedError()

    @property
    def outlets(self) -> List[str]:
        return ["outlet"]
