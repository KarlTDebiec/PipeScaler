#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Sorts image based on filename using a regular expression."""
from __future__ import annotations

import re
from logging import info
from typing import Optional

from pipescaler.core.pipelines import PipeObject
from pipescaler.core.pipelines.sorter import Sorter


class RegexSorter(Sorter):
    """Sorts image based on filename using a regular expression."""

    def __init__(self, regex: str) -> None:
        """Validate configuration and initialize.

        Arguments:
            regex: Sort as 'matched' if image name matches this regular expression
        """
        self.regex = re.compile(regex)

    def __call__(self, pipe_object: PipeObject) -> Optional[str]:
        """Get the outlet to which an image should be sorted.

        Arguments:
            pipe_object: Image to sort
        Returns:
            Outlet to which image should be sorted
        """
        if self.regex.match(pipe_object.location_name):
            outlet = "matched"
        else:
            outlet = "unmatched"
        info(f"{self}: '{pipe_object.location_name}' matches '{outlet}'")
        return outlet

    def __repr__(self) -> str:
        """Representation."""
        return f"{self.__class__.__name__}(regex={self.regex.pattern!r})"

    @property
    def outlets(self) -> tuple[str, ...]:
        """Outlets to which images may be sorted."""
        return ("matched", "unmatched")
