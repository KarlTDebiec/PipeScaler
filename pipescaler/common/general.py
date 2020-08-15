#!/usr/bin/env python
#   common/general.py
#
#   Copyright (C) 2017-2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
""""""
################################### MODULES ###################################
from inspect import currentframe, getframeinfo
from os import R_OK, access, getcwd
from os.path import basename, dirname, exists, expandvars, isfile, join
from readline import insert_text, redisplay, set_pre_input_hook
from typing import Any, Callable, Dict, Optional

# noinspection Mypy
from . import package_root


################################## FUNCTIONS ##################################
def embed_kw(verbosity: int = 2, **kwargs: Any) -> Dict[str, str]:
    """
    Prepares header for IPython prompt showing current location in code

    Use ``IPython.embed(**embed_kw())``.

    Args:
        verbosity (int): Level of verbose output
        **kwargs (Any): Additional keyword arguments

    Returns:
        Dict[str, str]: Keyword arguments to be passed to IPython.embed
    """
    frame = currentframe()
    if frame is None:
        raise ValueError()
    frameinfo = getframeinfo(frame.f_back)
    file = frameinfo.filename.replace(package_root, "")
    func = frameinfo.function
    number = frameinfo.lineno - 1
    header = ""
    if verbosity >= 1:
        header = f"IPython prompt in file {file}, function {func}," \
                 f" line {number}\n"
    if verbosity >= 2:
        header += "\n"
        with open(frameinfo.filename, "r") as infile:
            lines = [(i, line) for i, line in enumerate(infile)
                     if i in range(number - 5, number + 6)]
        for i, line in lines:
            header += f"{i:5d} {'>' if i == number else ' '} " \
                      f"{line.rstrip()}\n"

    return {"header": header}


def get_shell_type() -> Optional[str]:
    """
    Determines if inside IPython prompt

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
    Prompts user for input with pre-filled text

    Does not handle colored prompt correctly

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


def todo(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """
    Decorator used to annotate unimplemented functions in a useful way

    TODO: Remember why this seemed useful :)
    """

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError()

    return wrapper


def validate_infile(value: str) -> str:
    try:
        value = str(value)
    except ValueError:
        raise ValueError(f"'{value}' is of type '{type(value)}', not str")

    value = expandvars(value)
    directory = dirname(value)
    if directory == "":
        directory = getcwd()
    value = join(directory, basename(value))

    if not exists(value):
        raise ValueError(f"'{value}' does not exist")
    if not isfile(value):
        raise ValueError(f"'{value}' exists but is not a file")
    if not access(value, R_OK):
        raise ValueError(f"'{value}' exists but cannot be read")

    return value
