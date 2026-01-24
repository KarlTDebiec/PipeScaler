#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""File-related functions for testing."""

from __future__ import annotations

from os import getenv
from pathlib import Path

if getenv("PACKAGE_ROOT"):
    package_root = Path(str(getenv("PACKAGE_ROOT")))
else:
    from pipescaler.common import package_root


def get_test_input_path(name: str) -> Path:
    """Get full path of input file within test data directory.

    Arguments:
        name: Name of input file
    Returns:
        Full path to input file
    """
    path = Path(name)
    if str(path.parent) == ".":
        path = Path("basic") / path
    if path.suffix == "":
        path = path.with_suffix(".png")
    path = package_root.parent / "test" / "data" / "images" / path
    if not path.exists():
        raise FileNotFoundError()

    return path


def get_test_model_path(name: str) -> Path:
    """Get full path of model within test data directory.

    Arguments:
        name: Name of model
    Returns:
        Full path to model
    """
    path = Path(name)
    if str(path.parent) == ".":
        path = Path("WaifuUpConv7") / path
    if path.suffix == "":
        path = path.with_suffix(".pth")
    path = package_root.parent / "test" / "data" / "models" / path
    if getenv("CI") is None and not path.exists():
        raise FileNotFoundError()

    return path


def get_test_input_dir_path(name: str = "basic") -> Path:
    """Get path of subdirectory within test data directory.

    Arguments:
        name: Name of subdirectory
    Returns:
        Path to subdirectory
    """
    path = package_root.parent / "test" / "data" / "images" / name
    if not path.exists():
        raise FileNotFoundError()

    return path
