#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""File-related functions for testing."""
from os import environ, getenv
from os.path import dirname, join, normpath, sep, splitext
from pathlib import Path

from pipescaler.common import validate_input_file

if environ.get("PACKAGE_ROOT") is not None:
    package_root = getenv("PACKAGE_ROOT")
else:
    from pipescaler.common import package_root


def get_infile(name: str) -> Path:
    """Get full path of infile within test data directory.

    Arguments:
        name: Name of infile
    Returns:
        Full path to infile
    """
    path = Path(name)
    if str(path.parent) == ".":
        path = Path("basic").joinpath(path)
    if path.suffix == "":
        path = path.with_suffix(".png")
    path = Path(dirname(package_root)).joinpath("test", "data", "infiles", path)
    if not path.exists():
        raise FileNotFoundError()

    return path


def get_model_infile(name: str) -> Path:
    """Get full path of model within test data directory.

    Arguments:
        name: Name of model
    Returns:
        Full path to model
    """
    path = Path(name)
    if str(path.parent) == ".":
        path = Path("WaifuUpConv7").join(path)
    if path.suffix == "":
        path = path.with_suffix(".pth")
    path = Path(dirname(package_root)).joinpath("test","data","models",path)
    if getenv("CI") is None and not path.exists():
        raise FileNotFoundError()

    return path


def get_sub_directory(name: str) -> Path:
    """Get path of sub-directory within test data directory.

    Arguments:
        name: Name of sub-directory
    Returns:
        Path to sub-directory
    """
    path = Path(dirname(package_root)).joinpath("test", "data", "infiles", name)
    if not path.exists():
        raise FileNotFoundError()

    return path
