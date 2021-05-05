#!/usr/bin/env python
#   common/misc.py
#
#   Copyright (C) 2017-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""
General-purpose functions not tied to a particular project.

Last updated 2020-10-10.
"""
####################################### MODULES ########################################
from contextlib import contextmanager
from inspect import currentframe, getframeinfo
from os import remove
from os.path import basename, splitext
from readline import insert_text, set_pre_input_hook
from tempfile import NamedTemporaryFile
from typing import Dict, Iterator, Optional


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
    from . import package_root

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
        if shell == "InteractiveShellEmbed":
            # IPython in Jupyter Notebook using IPython.embed
            return shell
        if shell == "TerminalInteractiveShell":
            # IPython in terminal
            return shell
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
    from readline import redisplay

    def pre_input_hook() -> None:
        insert_text(str(prefill))
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
