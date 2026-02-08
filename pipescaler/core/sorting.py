#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Functions for sorting."""

from __future__ import annotations

from logging import error


def basic_sort(file_path: str) -> str:
    """Get file path in sortable format.

    Arguments:
        file_path: File path
    Returns:
        File path in sortable format
    """
    try:
        return "".join([f"{ord(c):03d}" for c in file_path.lower()])
    except ValueError as e:
        error(f"Error encountered while sorting {file_path}")
        raise e
