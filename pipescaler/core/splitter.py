#!/usr/bin/env python
#   pipescaler/core/splitter.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Base class for splitters"""
from __future__ import annotations

from abc import ABC
from typing import Any, Dict, List, Optional

from pipescaler.core.stage import Stage


class Splitter(Stage, ABC):
    """Base class for splitters"""

    def __init__(
        self, suffixes: Optional[Dict[str, str]] = None, **kwargs: Any
    ) -> None:
        """
        Validate and store static configuration

        Args:
            suffixes: Suffixes to add to split outfiles
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Store configuration
        if suffixes is not None:
            self.suffixes = suffixes
        else:
            self.suffixes = {outlet: outlet for outlet in self.outlets}

    def __call__(self, infile: str, **kwargs: Any) -> Dict[str, str]:
        """
        Split infile inout outfiles

        Args:
            infile: Input file
            **kwargs: Additional keyword arguments; including one argument for each
              outlet, whose key is the name of that outlet and whose value is the path
              to the associated outfile

        Returns:
            Dict whose keys are outlet names and whose values are the paths to each
            outlet's associated outfile
        """
        raise NotImplementedError()

    @property
    def inlets(self) -> List[str]:
        """Inlets that flow into stage"""
        return ["infile"]
