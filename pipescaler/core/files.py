#!/usr/bin/env python
#   pipescaler/core/files.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Core pipescaler functions for interacting with files"""
from __future__ import annotations

from os import listdir
from os.path import basename, splitext
from typing import Any, List, Optional, Set, Union

import yaml

from pipescaler.common import DirectoryNotFoundError, NotAFileError, validate_input_path


def parse_file_list(
    files: Union[str, List[str], Set[str]],
    absolute_paths: bool = False,
    exclusions: Optional[Union[str, List[str], Set[str]]] = None,
) -> Set[str]:
    """
    Parses a list of files from directories or text file.

    Args:
        files:
        absolute_paths: Whether or not to include absolute paths or just filenames
        exclusions:

    Returns:

    """
    # Prepare exclusion set
    exclusions_set = set()
    if exclusions is not None:
        exclusions_set = parse_file_list(exclusions, False)

    files_set = set()
    if files is None:
        return files_set
    if isinstance(files, str):
        files = [files]

    for file in files:
        try:
            try:
                # If file is a directory, add each file within it to file
                directory = validate_input_path(file, directory_ok=True, file_ok=False)
                directory_files = [
                    validate_input_path(f, default_directory=directory)
                    for f in listdir(directory)
                ]
                for directory_file in directory_files:
                    directory_file_base = splitext(basename(directory_file))[0]
                    if directory_file_base not in exclusions_set:
                        if absolute_paths:
                            files_set.add(directory_file)
                        else:
                            files_set.add(directory_file_base)
            except NotADirectoryError:
                try:
                    text_file = validate_input_path(
                        file, directory_ok=False, file_ok=True
                    )
                    with open(text_file, "r") as f:
                        for line in [line.strip() for line in f.readlines()]:
                            if line.startswith("#"):
                                continue
                            line_base = splitext(basename(line))[0]
                            if line_base not in exclusions_set:
                                if absolute_paths:
                                    files_set.add(line)
                                else:
                                    files_set.add(line_base)
                except NotAFileError:
                    if absolute_paths:
                        files_set.add(file)
                    else:
                        files_set.add(splitext(basename(file))[0])
        except (FileNotFoundError, DirectoryNotFoundError):
            files_set.add(file)

    files_set -= exclusions_set

    return files_set


def read_yaml(infile: str) -> Any:
    """
    Reads a yaml file and returns the contents.

    Args:
        infile: Path to input file

    Returns:
        Loaded yaml data structure
    """
    with open(validate_input_path(infile), "r") as f:
        return yaml.load(f, Loader=yaml.SafeLoader)
