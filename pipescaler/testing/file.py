#!/usr/bin/env python
#  Copyright 2020-2023 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""File-related functions for testing."""
from __future__ import annotations

from os import getenv
from pathlib import Path

if getenv("PACKAGE_ROOT"):
    package_root = Path(str(getenv("PACKAGE_ROOT")))
else:
    from pipescaler.common import package_root


def get_test_infile_path(name: str) -> Path:
    """Get full path of infile within test data directory.

    Arguments:
        name: Name of infile
    Returns:
        Full path to infile
    """
    path = Path(name)
    if str(path.parent) == ".":
        path = Path("basic") / path
    if path.suffix == "":
        path = path.with_suffix(".png")
    path = package_root.parent / "test" / "data" / "infiles" / path
    if not path.exists():
        raise FileNotFoundError()

    return path


def get_test_model_infile_path(name: str) -> Path:
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


def get_test_infile_directory_path(name: str = "basic") -> Path:
    """Get path of subdirectory within test data directory.

    Arguments:
        name: Name of subdirectory
    Returns:
        Path to subdirectory
    """
    path = package_root.parent / "test" / "data" / "infiles" / name
    if not path.exists():
        raise FileNotFoundError()

    return path
