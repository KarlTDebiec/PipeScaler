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


def get_infile(name: str) -> str:
    """Get full path of infile within test data directory.

    Args:
        name: Name of infile
    Returns:
        Full path to infile
    """
    base_directory = join(dirname(package_root), "test", "data", "infiles")
    split_name = normpath(name).split(sep)
    if len(split_name) == 1:
        sub_directory = "basic"
    else:
        sub_directory = join(*split_name[:-1])
    filename = split_name[-1]
    if splitext(filename)[-1] == "":
        filename = f"{filename}.png"

    return validate_input_file(join(base_directory, sub_directory, filename))


def get_model_infile(name: str) -> str:
    """Get full path of model within test data directory.

    Args:
        name: Name of model
    Returns:
        Full path to model
    """
    base_directory = join(dirname(package_root), "test", "data", "models")
    split_name = normpath(name).split(sep)
    if len(split_name) == 1:
        sub_directory = "WaifuUpConv7"
    else:
        sub_directory = join(*split_name[:-1])
    filename = split_name[-1]
    if splitext(filename)[-1] == "":
        filename = f"{filename}.pth"

    infile = join(base_directory, sub_directory, filename)
    if getenv("CI") is None:
        infile = validate_input_file(infile)

    return infile


def get_sub_directory(name: str) -> Path:
    """Get path of sub-directory within test data directory.

    Args:
        name: Name of sub-directory
    Returns:
        Path to sub-directory
    """
    return Path(dirname(package_root)).joinpath("test", "data", "infiles", name)
