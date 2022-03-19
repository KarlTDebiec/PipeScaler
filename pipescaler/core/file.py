#!/usr/bin/env python
#   pipescaler/core/file.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Core functions for interacting with files"""
from __future__ import annotations

from mimetypes import guess_type
from os import listdir
from os.path import basename, dirname, isabs, join, splitext
from typing import Any, List, Optional, Set, Union

import yaml

from pipescaler.common import DirectoryNotFoundError, NotAFileError, validate_input_path


def get_files_in_directory(
    directory: str,
    style: str = "base",
    exclusions: Optional[Union[str, List[str], Set[str]]] = None,
) -> Set[str]:
    """
    Get filenames within provided directory.

    Arguments:
        directory: Directory from which to get filenames
        style: Style in which to get filenames, may be 'absolute' for the complete
          path, 'base' for the filename excluding extension, and 'full' for the filename
          including extension
        exclusions: Base names of files to exclude
    Returns:
        Filenames in configured style
    """
    if style not in ["absolute", "base", "full"]:
        raise ValueError()
    if exclusions is None:
        exclusions = set()
    files = set()

    directory = validate_input_path(directory, directory_ok=True, file_ok=False)
    for filename in listdir(directory):
        absolute = validate_input_path(filename, default_directory=directory)
        base = splitext(basename(filename))[0]
        if base not in exclusions:
            if style == "absolute":
                files.add(absolute)
            elif style == "base":
                files.add(base)
            else:
                files.add(filename)

    return files


def get_files_in_text_file(
    text_file: str,
    style: str = "base",
    exclusions: Optional[Union[str, List[str], Set[str]]] = None,
) -> Set[str]:
    """
    Get filenames within provided text file.

    Arguments:
        text_file: Text file from which to get filenames
        style: Style in which to get filenames, may be 'absolute' for the complete
          path, 'base' for the filename excluding extension, and 'full' for the filename
          including extension
        exclusions: Base names of files to exclude
    Returns:
        Filenames in configured style
    """
    if style not in ["absolute", "base", "full"]:
        raise ValueError()
    if exclusions is None:
        exclusions = set()
    files = set()

    text_file = validate_input_path(text_file)
    with open(text_file, "r", encoding="utf8") as infile:
        filenames = [
            line.strip() for line in infile.readlines() if not line.startswith("#")
        ]
    for filename in filenames:
        base = splitext(basename(filename))[0]
        if base not in exclusions:
            if style == "absolute":
                absolute = validate_input_path(
                    filename, default_directory=join(dirname(text_file), base)
                )
                files.add(absolute)
            elif style == "base":
                files.add(base)
            else:
                files.add(filename)

    return files


def get_files(
    sources: Union[str, List[str]],
    style: str = "base",
    exclusions: Optional[Set[str]] = None,
) -> Set[str]:
    """
    Get filenames from provided sources, which may be either directories or text files.

    Arguments:
        sources: Directories and text files from which to get filenames
        style: Style in which to get filenames, may be 'absolute' for the complete
          path, 'base' for the filename excluding extension, and 'full' for the filename
          including extension
        exclusions: Base filenames to exclude
    Returns:
        Filenames in configured style
    """
    if style not in ["absolute", "base", "full"]:
        raise ValueError()
    if exclusions is None:
        exclusions = set()
    if isinstance(sources, str):
        sources = [sources]
    files = set()

    def get_file(file_source: str) -> Optional[str]:
        """
        Gets a filename in configured style.

        Arguments:
            file_source: Filename
        Returns:
            Filename in configured style
        """
        if isabs(file_source):
            filename = basename(file_source)
        else:
            filename = file_source
        base = splitext(basename(filename))[0]
        if base not in exclusions:
            if style == "absolute":
                if isabs(file_source):
                    absolute = file_source
                else:
                    absolute = validate_input_path(filename)
                return absolute
            if style == "base":
                return base
            return filename
        return None

    for source in sources:
        try:
            directory = validate_input_path(source, directory_ok=True, file_ok=False)
            files |= get_files_in_directory(directory, style, exclusions)
        except (DirectoryNotFoundError, NotADirectoryError):
            try:
                file = validate_input_path(source, directory_ok=False, file_ok=True)
                guessed_type = guess_type(file)[0]
                if guessed_type in ["image/png"]:
                    files.add(get_file(source))
                else:
                    files |= get_files_in_text_file(file, style, exclusions)
            except (FileNotFoundError, NotAFileError, UnicodeDecodeError):
                continue

    return files


def read_yaml(infile: str) -> Any:
    """
    Reads a yaml file and returns the contents.

    Arguments:
        infile: Path to input file
    Returns:
        Loaded yaml data structure
    """
    with open(validate_input_path(infile), "r", encoding="utf8") as yaml_file:
        return yaml.load(yaml_file, Loader=yaml.SafeLoader)
