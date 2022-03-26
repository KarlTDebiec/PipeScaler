#!/usr/bin/env python
#   pipescaler/testing/file.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""File-related functions for testing"""
from os import environ, getenv
from os.path import dirname, join, normpath, sep, splitext

from pipescaler.common import validate_input_directory, validate_input_file

if environ.get("PACKAGE_ROOT") is not None:
    package_root = getenv("PACKAGE_ROOT")
else:
    from pipescaler.common import package_root


def get_infile(name: str):
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


def get_model_infile(name: str):
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


def get_script(filename: str, sub_directory: str = "scripts"):
    if splitext(filename)[-1] == "":
        filename = f"{filename}.py"
    return validate_input_file(join(package_root, normpath(sub_directory), filename))


def get_sub_directory(sub_directory: str):
    base_directory = join(dirname(package_root), "test", "data", "infiles")

    return validate_input_directory(join(base_directory, sub_directory))
