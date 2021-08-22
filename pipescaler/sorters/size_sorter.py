#!/usr/bin/env python
#   pipescaler/sorters/size_sorter.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
""""""
from __future__ import annotations

from logging import info
from typing import Any, Dict, List

from PIL import Image

from pipescaler.common import validate_int
from pipescaler.core import Sorter


class SizeSorter(Sorter):

    # region Builtins
    def __init__(self, cutoff: int = 32, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        # Store configuration
        self.cutoff = validate_int(cutoff, min_value=1)

    def __call__(self, infile: str) -> str:
        # Read image
        image = Image.open(infile)

        if image.size[0] < self.cutoff or image.size[1] < self.cutoff:
            info(f"{self}: {infile}'s smallest dimension is less than{self.cutoff}")
            return "less_than"
        else:
            info(
                f"{self}: {infile}'s smallest dimension is greater than or equal to"
                f" {self.cutoff}"
            )
            return "greater_than_or_equal_to"

    # endregion

    # region Properties

    @property
    def outlets(self):
        return ["less_than", "greater_than_or_equal_to"]

    # endregion
