#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Sorts image based on filename using a regular expression."""
from __future__ import annotations

import re
from logging import info

from pipescaler.core.pipelines import PipeImage
from pipescaler.core.pipelines.sorter import Sorter


class RegexSorter(Sorter):
    """Sorts image based on filename using a regular expression."""

    def __init__(self, regex: str) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            regex: Sort as 'matched' if image name matches this regular expression
        """
        self.regex = re.compile(regex)

    def __call__(self, pipe_image: PipeImage) -> str:
        if self.regex.match(pipe_image.name):
            outlet = "matched"
        else:
            outlet = "unmatched"
        info(f"{self}: {pipe_image.name} matches {outlet}")
        return outlet

    @property
    def outlets(self) -> tuple[str, ...]:
        """Outlets that flow out of stage."""
        return ("matched", "unmatched")