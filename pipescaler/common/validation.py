#!/usr/bin/env python
#   common/validation.py
#
#   Copyright (C) 2017-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""
General-purpose validation functions not tied to a particular project.

Last updated 2020-10-10.
"""
####################################### MODULES ########################################
from os import R_OK, W_OK, access, getcwd
from os.path import (
    defpath,
    dirname,
    exists,
    expandvars,
    isabs,
    isdir,
    isfile,
    join,
)
from shutil import which
from typing import Any, Optional, Tuple

from .exceptions import (
    ArgumentConflictError,
    DirectoryNotFoundError,
    ExecutableNotFoundError,
    NotAFileError,
    NotAFileOrDirectoryError,
)


###################################### FUNCTIONS #######################################
def validate_executable(value: Any) -> str:
    try:
        value = str(value)
    except ValueError:
        raise TypeError(f"'{value}' is of type '{type(value)}', not str")

    if which(value) is None:
        raise ExecutableNotFoundError(f"'{value}' executable not found in '{defpath}'")
    value = which(value)

    return value


def validate_float(
    value: Any, min_value: Optional[float] = None, max_value: Optional[float] = None
) -> float:
    if min_value is not None and max_value is not None and (min_value >= max_value):
        raise ArgumentConflictError("min_value must be greater than max_value")

    try:
        value = float(value)
    except ValueError:
        raise TypeError(f"'{value}' is of type '{type(value)}', not float")

    if min_value is not None and value < min_value:
        raise ValueError(f"'{value}' is less than minimum value of '{min_value}'")
    if max_value is not None and value > max_value:
        raise ValueError(f"'{value}' is greater than maximum value of '{max_value}'")

    return value


def validate_input_path(
    value: Any,
    file_ok: bool = True,
    directory_ok: bool = False,
    default_directory: Optional[str] = None,
) -> str:
    """
    Validates an input path and makes it absolute.

    Args:
        value (Any): Provided input path
        file_ok (bool): Whether or not file paths are permissible
        directory_ok (bool): Whether or not directory paths are permissible
        default_directory (Optional[str]): Default directory to prepend to *value* if
          not absolute (default: current working directory)

    Returns:
        str: Absolute path to input file or directory

    Raises:
        ValueError: If input path is not valid
    """
    if not file_ok and not directory_ok:
        raise ArgumentConflictError(
            "both file and directory paths may not be prohibited"
        )
    if default_directory is None:
        default_directory = getcwd()

    try:
        value = str(value)
    except ValueError:
        raise TypeError(f"'{value}' is of type '{type(value)}', not str")

    value = expandvars(value)
    if not isabs(value):
        value = join(default_directory, value)

    if not exists(value):
        raise FileNotFoundError(f"'{value}' does not exist")
    if file_ok and not directory_ok and not isfile(value):
        raise NotAFileError(f"'{value}' is not a file")
    if not file_ok and directory_ok and not isdir(value):
        raise NotADirectoryError(f"'{value}' is not a directory")
    if not isfile(value) and not isdir(value):
        raise NotAFileOrDirectoryError(f"'{value}' is not a file or directory")
    if not access(value, R_OK):
        raise PermissionError(f"'{value}' cannot be read")

    return value


def validate_int(
    value: Any,
    min_value: Optional[int] = None,
    max_value: Optional[int] = None,
    choices: Optional[Tuple[int]] = None,
) -> int:
    if min_value is not None and max_value is not None and (min_value >= max_value):
        raise ArgumentConflictError("min_value must be greater than max_value")

    try:
        value = int(value)
    except ValueError:
        raise TypeError(f"'{value}' is of type '{type(value)}', not int")

    if min_value is not None and value < min_value:
        raise ValueError(f"'{value}' is less than minimum value of '{min_value}'")
    if max_value is not None and value > max_value:
        raise ValueError(f"'{value}' is greater than maximum value of '{max_value}'")
    if choices is not None and value not in choices:
        raise ValueError(f"'{value}' is not one of {choices}")

    return value


def validate_output_path(
    value: Any,
    file_ok: bool = True,
    directory_ok: bool = False,
    default_directory: Optional[str] = None,
) -> str:
    """
    Validates an output path and makes it absolute.

    TODO: option to try to create directory if it does not exist

    Args:
        value (Any): Provided output path
        file_ok (bool): Whether or not file paths are permissible
        directory_ok (bool): Whether or not directory paths are permissible
        default_directory (Optional[str]): Default directory to prepend to *value* if
          not absolute (default: current working directory)

    Returns:
        str: Absolute path to output file or directory

    Raises:
        ValueError: If output path is not valid
    """
    if not file_ok and not directory_ok:
        raise ArgumentConflictError(
            "both file and directory paths may not be prohibited"
        )
    if default_directory is None:
        default_directory = getcwd()

    try:
        value = str(value)
    except ValueError:
        raise TypeError(f"'{value}' is of type '{type(value)}', not str")

    value = expandvars(value)
    if not isabs(value):
        value = join(default_directory, value)

    if exists(value):
        if file_ok and not directory_ok and not isfile(value):
            raise NotAFileError(f"'{value}' is not a file")
        if not file_ok and directory_ok and not isdir(value):
            raise NotADirectoryError(f"'{value}' is not a directory")
        if not isfile(value) and not isdir(value):
            raise NotAFileOrDirectoryError(f"'{value}' is not a file or directory")
        if not access(value, W_OK):
            raise PermissionError(f"'{value}' cannot be written")
    else:
        directory = dirname(value)
        if not exists(directory):
            raise DirectoryNotFoundError(f"'{directory}' does not exist")
        if not isdir(directory):
            raise NotADirectoryError(f"'{directory}' is not a directory")
        if not access(directory, W_OK):
            raise PermissionError(f"'{directory}' cannot be written")

    return value


def validate_type(value: Any, cls: Any) -> Any:
    if not isinstance(value, cls):
        raise TypeError(f"'{value}' is of type '{type(value)}', not {cls.__name__}")
    return value
