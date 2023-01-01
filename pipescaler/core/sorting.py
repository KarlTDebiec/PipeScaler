#!/usr/bin/env python
#  Copyright 2020-2023 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Functions for sorting."""
from __future__ import annotations

from logging import error


def basic_sort(filename: str) -> str:
    """Sort filenames."""
    try:
        return "".join([f"{ord(c):03d}" for c in filename.lower()])
    except ValueError as e:
        error(f"Error encountered while sorting {filename}")
        raise e
