#!/usr/bin/env python
#   pipescaler/core/merger.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Base class for merger stages"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List, Optional

from pipescaler.core.stage import Stage


class Merger(Stage, ABC):
    """Base class for merger stages"""

    def __init__(
        self,
        suffix: Optional[str] = None,
        trim_suffixes: Optional[List[str]] = None,
        **kwargs: Any
    ) -> None:
        """
        Validate and store static configuration

        Args:
            suffix: Suffix to add to merged outfiles
            trim_suffixes: Suffixes to trim from merged outfiles
            **kwargs: Additional keyword arguments
        """
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
        """
        Merge infiles into an outfile

        Args:
            outfile: Path to output file
            **kwargs: Additional keyword arguments; including one argument for each
              inlet, whose key is the name of that inlet and whose value is the path to
              the associated infile
        """
        raise NotImplementedError()

    @property
    def outlets(self) -> List[str]:
        """Outlets that flow out of stage"""
        return ["outlet"]
