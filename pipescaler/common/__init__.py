#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""General-purpose code not tied to a particular project.

Utilities in this package depend only on the standard library and one another.

Package hierarchy (modules may import from any above):
* csv / described_enum / duration / exceptions / file / logs / subprocess
* exception / command_line_interface / validation
* argument_parsing / cli / testing

The legacy exception module re-exports the classes defined in exceptions.
"""

from __future__ import annotations

from pathlib import Path

from pipescaler.common.command_line_interface import CLIKwargs, CommandLineInterface
from pipescaler.common.exceptions import (
    ArgumentConflictError,
    DirectoryExistsError,
    DirectoryNotFoundError,
    ExecutableNotFoundError,
    GetterError,
    IsAFileError,
    NotAFileError,
    NotAFileOrDirectoryError,
    UnsupportedPlatformError,
)

package_root = Path(__file__).resolve().parent.parent
"""Absolute path of the package containing this submodule.

If this file is '/path/to/package/common/__init__.py', the value is
'/path/to/package'.
"""

__all__ = [
    "ArgumentConflictError",
    "CLIKwargs",
    "CommandLineInterface",
    "DirectoryExistsError",
    "DirectoryNotFoundError",
    "ExecutableNotFoundError",
    "GetterError",
    "IsAFileError",
    "NotAFileError",
    "NotAFileOrDirectoryError",
    "UnsupportedPlatformError",
    "package_root",
]
