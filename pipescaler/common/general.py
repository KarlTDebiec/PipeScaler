#!/usr/bin/env python
#   common/general.py
#
#   Copyright (C) 2017-2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""
General-purpose functions not tied to a particular project.

Last updated 2020-09-10.
"""
####################################### MODULES ########################################
from contextlib import contextmanager
from inspect import currentframe, getframeinfo
from os import R_OK, W_OK, access, getcwd, remove
from os.path import (
    basename,
    defpath,
    dirname,
    exists,
    expandvars,
    isabs,
    isdir,
    isfile,
    join,
    splitext,
)
from readline import insert_text, redisplay, set_pre_input_hook
from shutil import which
from tempfile import NamedTemporaryFile
from typing import Any, Dict, Iterator, Optional

from . import package_root


###################################### FUNCTIONS #######################################
def embed_kw(verbosity: int = 2) -> Dict[str, str]:
    """
    Prepares header for IPython prompt showing current location in code.

    Use ``IPython.embed(**embed_kw())``.

    Args:
        verbosity (int): Level of verbose output

    Returns:
        Dict[str, str]: Keyword arguments to be passed to IPython.embed
    """
    frame = currentframe()
    if frame is None:
        raise ValueError()
    # noinspection Mypy
    frameinfo = getframeinfo(frame.f_back)
    file = frameinfo.filename.replace(package_root, "")
    func = frameinfo.function
    number = frameinfo.lineno - 1
    header = ""
    if verbosity >= 1:
        header = f"IPython prompt in file {file}, function {func}," f" line {number}\n"
    if verbosity >= 2:
        header += "\n"
        with open(frameinfo.filename, "r") as infile:
            lines = [
                (i, line)
                for i, line in enumerate(infile)
                if i in range(number - 5, number + 6)
            ]
        for i, line in lines:
            header += f"{i:5d} {'>' if i == number else ' '} " f"{line.rstrip()}\n"

    return {"header": header}


def get_ext(infile: str) -> str:
    return splitext(basename(infile))[1].strip(".")


def get_name(infile: str) -> str:
    return splitext(basename(infile))[0]


def get_shell_type() -> Optional[str]:
    """
    Determines if inside IPython prompt.

    Returns:
        Optional[str]: Type of shell in use, or None if not in a shell
    """
    try:
        # noinspection Mypy
        shell = str(get_ipython().__class__.__name__)
        if shell == "ZMQInteractiveShell":
            # IPython in Jupyter Notebook
            return shell
        elif shell == "InteractiveShellEmbed":
            # IPython in Jupyter Notebook using IPython.embed
            return shell
        elif shell == "TerminalInteractiveShell":
            # IPython in terminal
            return shell
        else:
            # Other
            return shell
    except NameError:
        # Not in IPython
        return None


def input_prefill(prompt: str, prefill: str) -> str:
    """
    Prompts user for input with pre-filled text.

    Does not handle colored prompt correctly.

    TODO: Does this block CTRL-D?

    Args:
        prompt (str): Prompt to present to user
        prefill (str): Text to prefill for user

    Returns:
        str: Text inputted by user
    """

    def pre_input_hook() -> None:
        insert_text(prefill)
        redisplay()

    set_pre_input_hook(pre_input_hook)
    result = input(prompt)
    set_pre_input_hook()

    return result


@contextmanager
def temporary_filename(suffix: Optional[str] = None) -> Iterator[str]:
    """
    Provides a temporary filename; use with 'with'.

    Args:
        suffix (Optional[str]): Suffix (extension) for temporary filename

    Yields:
        str: Temporary filename
    """
    f = None
    try:
        f = NamedTemporaryFile(delete=False, suffix=suffix)
        f.close()
        yield f.name
    finally:
        if f is not None:
            remove(f.name)


def validate_executable(value: Any) -> str:
    try:
        value = str(value)
    except ValueError:
        raise ValueError(f"'{value}' is of type '{type(value)}', not str")

    if which(value) is None:
        raise ValueError(f"'{value}' executable not found in '{defpath}'")
    value = which(value)

    return value


def validate_float(
    value: Any, min_value: Optional[float] = None, max_value: Optional[float] = None
) -> float:
    if min_value is not None and max_value is not None and (min_value >= max_value):
        raise ValueError("min_value must be greater than max_value")

    try:
        value = float(value)
    except ValueError:
        raise ValueError(f"'{value}' is of type '{type(value)}', not float")

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
        raise ValueError("both file and directory paths may not be prohibited")
    if default_directory is None:
        default_directory = getcwd()

    try:
        value = str(value)
    except ValueError:
        raise ValueError(f"'{value}' is of type '{type(value)}', not str")

    value = expandvars(value)
    if not isabs(value):
        value = join(default_directory, value)

    if not exists(value):
        raise ValueError(f"'{value}' does not exist")
    elif file_ok and not directory_ok and not isfile(value):
        raise ValueError(f"'{value}' is not a file")
    elif not file_ok and directory_ok and not isdir(value):
        raise ValueError(f"'{value}' is not a directory")
    elif not isfile(value) and not isdir(value):
        raise ValueError(f"'{value}' is not a file or directory")
    elif not access(value, R_OK):
        raise ValueError(f"'{value}' cannot be read")

    return value


def validate_int(
    value: Any, min_value: Optional[int] = None, max_value: Optional[int] = None
) -> int:
    if min_value is not None and max_value is not None and (min_value >= max_value):
        raise ValueError("min_value must be greater than max_value")

    try:
        value = int(value)
    except ValueError:
        raise ValueError(f"'{value}' is of type '{type(value)}', not int")

    if min_value is not None and value < min_value:
        raise ValueError(f"'{value}' is less than minimum value of '{min_value}'")
    if max_value is not None and value > max_value:
        raise ValueError(f"'{value}' is greater than maximum value of '{max_value}'")
    return value


def validate_output_path(
    value: Any,
    file_ok: bool = True,
    directory_ok: bool = False,
    default_directory: Optional[str] = None,
) -> str:
    """
    Validates an output path and makes it absolute.

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
        raise ValueError("both file and directory paths may not be prohibited")
    if default_directory is None:
        default_directory = getcwd()

    try:
        value = str(value)
    except ValueError:
        raise ValueError(f"'{value}' is of type '{type(value)}', not str")

    value = expandvars(value)
    if not isabs(value):
        value = join(default_directory, value)

    if exists(value):
        if file_ok and not directory_ok and not isfile(value):
            raise ValueError(f"'{value}' is not a file")
        elif not file_ok and directory_ok and not isdir(value):
            raise ValueError(f"'{value}' is not a directory")
        elif not isfile(value) and not isdir(value):
            raise ValueError(f"'{value}' is not a file or directory")
        elif not access(value, W_OK):
            raise ValueError(f"'{value}' cannot be written")
    else:
        directory = dirname(value)
        if not exists(directory):
            raise ValueError(f"'{directory}' does not exist")
        elif not isdir(directory):
            raise ValueError(f"'{directory}' is not a directory")
        if not access(directory, W_OK):
            raise ValueError(f"'{directory}' cannot be written")

    return value


def validate_type(value: Any, cls: Any) -> Any:
    if not isinstance(value, cls):
        raise ValueError(f"'{value}' is of type '{type(value)}', not {cls.__name__}")
    return value
