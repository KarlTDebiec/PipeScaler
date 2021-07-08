#!/usr/bin/env python
#   pipescaler/core/misc.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from os import listdir
from os.path import basename, splitext
from typing import List, Optional, Set, Union

from pipescaler.common import NotAFileError, validate_input_path


###################################### FUNCTIONS #######################################
def parse_file_list(
    files: Optional[Union[str, List[str]]],
    full_paths: bool = False,
    exclusions: Optional[Union[str, List[str]]] = None,
) -> Set[str]:
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
                directory = validate_input_path(file, directory_ok=True, file_ok=False)
                directory_files = [
                    validate_input_path(f, default_directory=directory)
                    for f in listdir(directory)
                ]
                for directory_file in directory_files:
                    directory_file_base = splitext(basename(directory_file))[0]
                    if directory_file_base not in exclusions_set:
                        if full_paths:
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
                                if full_paths:
                                    files_set.add(line)
                                else:
                                    files_set.add(line_base)
                except NotAFileError:
                    if full_paths:
                        files_set.add(file)
                    else:
                        files_set.add(splitext(basename(file))[0])
        except FileNotFoundError:
            files_set.add(file)

    files_set -= exclusions_set

    return files_set
