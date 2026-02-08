#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PipeScaler root package; contains general code not specific to any kind of object."""

from __future__ import annotations

from .file_scanner import FileScanner

__all__ = [
    "FileScanner",
]
