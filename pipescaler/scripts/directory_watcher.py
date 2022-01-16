#!/usr/bin/env python
#   pipescaler/scripts/directory_watcher.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Watches files in a directory"""
from __future__ import annotations

import re
from logging import debug, info
from os import makedirs, remove, rmdir
from os.path import basename, isdir, isfile, join, splitext
from shutil import copy, move
from time import sleep
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from pipescaler.common import (
    DirectoryNotFoundError,
    validate_input_directory,
    validate_output_directory,
    validate_output_file,
)
from pipescaler.core import ConfigurableCommandLineTool, get_files
from pipescaler.util import ScaledPairIdentifier

pd.set_option(
    "display.max_rows", None, "display.max_columns", None, "display.width", 140
)


class DirectoryWatcher(ConfigurableCommandLineTool):
    """Watches files in a directory"""

    exclusions = {".DS_Store", "desktop"}

    def __init__(
        self,
        input_directory: Union[str, List[str]],
        copy_directory: str,
        move_directory: str,
        rules: List[List[str, str]],
        reviewed_directory: Optional[Union[str, List[str]]] = None,
        ignore_directory: Optional[Union[str, List[str]]] = None,
        scaled_directory: Optional[str] = None,
        remove_directory: Optional[str] = None,
        observed_filenames_infile: Optional[str] = None,
        observed_filenames_outfile: Optional[str] = None,
        scaled_pair_identifier: Optional[Dict[str:Any]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Validate and store static configuration

        Arguments:
            input_directory: Directory or directories from which to read input files
            copy_directory: Directory to which to copy images that match 'copy' rule
            move_directory: Directory to which to move images that match 'move' rule
            rules: Rules by which to process images
            reviewed_directory: Directory or directories of reviewed images
            ignore_directory: Directory or directories of reviewed images to ignore
            observed_filenames_infile: Text file from which to read list of observed
              files
            observed_filenames_outfile: Text file to which to write list of observed
              files
            remove_directory: Directory of reviewed images to remove from input
              directory or directories
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        def validate_input_directories(input_directories: Union[str, List[str]]):
            """Validate input directory paths and make them absolute"""
            if isinstance(input_directories, str):
                input_directories = [input_directories]
            return [validate_input_directory(d) for d in input_directories]

        # Validate input and output directory and file paths
        self.ignore_directories = []
        """Directories containing files which should be ignored"""
        if ignore_directory is not None:
            self.ignore_directories = validate_input_directories(ignore_directory)
        self.input_directories = validate_input_directories(input_directory)
        """Directories from which to read input files"""
        self.copy_directory = validate_output_directory(copy_directory)
        """Directory to which to copy images that match 'copy' rule"""
        self.move_directory = validate_output_directory(move_directory)
        """Directory to which to move images that match 'move' rule"""
        self.remove_directory = None
        """Directory containing files which should be removed from input directories"""
        if remove_directory is not None:
            try:
                self.remove_directory = validate_input_directory(remove_directory)
            except DirectoryNotFoundError:
                pass
        self.reviewed_directories = []
        """Directories containing files which have been reviewed"""
        if reviewed_directory is not None:
            self.reviewed_directories = validate_input_directories(reviewed_directory)
        self.scaled_directory = None
        """Directory containing files which are rescaled from other files"""
        if scaled_directory is not None:
            self.scaled_directory = validate_output_directory(scaled_directory)

        # Prepare filename data structures
        self.reviewed_filenames = get_files(self.reviewed_directories, style="base")
        """Base filenames of images in classified directories"""
        self.ignore_filenames = get_files(self.ignore_directories, style="base")
        """Base filenames of images to ignore"""
        self.rules = [(re.compile(regex), action) for regex, action in rules]
        """Rules by which to classify images"""
        absolute_filenames = get_files(self.input_directories, style="absolute")
        if self.scaled_directory is not None:
            absolute_filenames.update(
                get_files(self.scaled_directory, style="absolute")
            )
        absolute_filenames = sorted(list(absolute_filenames))
        self.filenames = {splitext(basename(f))[0]: f for f in absolute_filenames}
        """Input filenames; keys are base names and values are absolute paths"""
        info(f"Found {len(self.filenames)} infiles in {self.input_directories}")

        # Initialize scaled pair identifier
        self.scaled_pair_identifier = None
        """Scaled pair identifier"""
        if scaled_pair_identifier is not None:
            self.scaled_pair_identifier = ScaledPairIdentifier(
                filenames=self.filenames, **scaled_pair_identifier
            )

        # Initialize observed filename lister
        self.observed_filenames = set()
        if observed_filenames_infile is not None:
            self.observed_filenames = get_files(observed_filenames_infile, style="base")
        self.observed_filenames_outfile = None
        """Text file to which to write observed filenames"""
        if observed_filenames_outfile is not None:
            self.observed_filenames_outfile = validate_output_file(
                observed_filenames_outfile
            )

    def __call__(self, **kwargs: Any) -> Any:
        """
        Perform operations

        Arguments:
            **kwargs: Additional keyword arguments
        """

        # Prepare to run
        self.remove_files_in_copy_directory()
        if self.remove_directory is not None:
            self.remove_files_in_remove_directory()

        # Search for scaled image pairs
        if self.scaled_pair_identifier is not None:
            self.scaled_pair_identifier.identify_pairs()
        self.process_files_in_input_directories()
        # self.write_observed_filenames_to_outfile()

        # Watch for new files
        # self.watch_new_files_in_input_directory()

    def remove_files_in_copy_directory(self):
        """
        Remove existing files in the copy directory; which is refreshed from the input
        directory with each run
        """
        if isdir(self.copy_directory):
            for filename in get_files(self.copy_directory, style="absolute"):
                remove(filename)

    def remove_files_in_remove_directory(self):
        """
        Remove existing files in the remove directory, as well as their source files in
        the input directories; afterwards remove the remove directory itself
        """
        if self.remove_directory is not None:
            remove_filenames = get_files(self.remove_directory, style="full")
            for filename in remove_filenames:
                for input_directory in self.input_directories:
                    if isfile(join(input_directory, filename)):
                        remove(join(input_directory, filename))
                        info(
                            f"'{filename}' removed from input directory "
                            f"'{input_directory}'"
                        )
                if isfile(join(self.remove_directory, filename)):
                    remove(join(self.remove_directory, filename))
                    info(f"'{filename}' removed from remove directory")
            rmdir(self.remove_directory)
            info(f"'{self.remove_directory}' removed")

    def move_children_to_scaled_directory(self):
        """Move children to scaled directory"""
        for child_filename in self.scaled_directory:
            child = basename(self.filenames[child_filename])
            for reviewed_directory in self.reviewed_directories:
                if isfile(join(reviewed_directory, child)):
                    move(
                        join(reviewed_directory, child),
                        join(self.scaled_directory, child),
                    )
                    info(
                        f"'{child}' moved from reviewed directory '{reviewed_directory}' "
                        f"to scaled directory '{self.scaled_directory}'"
                    )

    def process_files_in_input_directories(self):
        """Process files in input directories"""
        for filename in self.filenames:
            self.perform_operation_for_filename(filename)

    def perform_operation_for_filename(self, filename):
        """Perform operations for filename"""
        status = self.select_operation_for_filename(filename)
        if status == "known":
            self.observed_filenames.add(filename)
            debug(f"'{filename}' known")
        elif status == "ignore":
            debug(f"'{filename}' ignored")
        elif status == "copy":
            if not isdir(self.copy_directory):
                makedirs(self.copy_directory)
                info(f"'{self.copy_directory}' created")
            copy(
                f"{self.input_directories}/{filename}.png",
                f"{self.copy_directory}/{filename}.png",
            )
            info(f"'{filename}' copied to '{self.copy_directory}'")
        elif status == "move":
            if not isdir(self.move_directory):
                makedirs(self.move_directory)
                info(f"'{self.move_directory}' created")
            move(
                f"{self.input_directories}/{filename}.png",
                f"{self.move_directory}/{filename}.png",
            )
            info(f"'{filename}' moved to '{self.move_directory}'")
        elif status == "remove":
            remove(f"{self.input_directories}/{filename}.png")
            info(f"'{filename}' deleted")
        else:
            raise ValueError()

    def select_operation_for_filename(self, filename):
        """Select operation for filename"""

        if filename in self.reviewed_filenames:
            return "known"

        for rule in self.rules:
            regex = next(iter(rule))
            action = rule[next(iter(rule))]
            if regex.match(filename):
                return action

        return "copy"

    def watch_new_files_in_input_directory(self):
        """Watch new files in input directory"""
        try:
            from watchdog.events import FileSystemEventHandler
            from watchdog.observers import Observer
        except ImportError as e:
            raise e

        class FileCreatedEventHandler(FileSystemEventHandler):
            """event handler"""

            def __init__(self, host) -> None:
                self.host = host

            def on_created(self, event):
                """action"""
                filename = splitext(basename(event.key[1]))[0]
                self.host.perform_operation_for_filename(filename)

        event_handler = FileCreatedEventHandler(self)
        observer = Observer()
        observer.schedule(event_handler, self.input_directories[0])
        observer.start()
        try:
            while True:
                sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    def write_observed_filenames_to_outfile(self):
        """Write observed filenames to outfile"""
        if self.observed_filenames_outfile is not None:
            with open(self.observed_filenames_outfile, "w") as outfile:
                for filename in sorted(list(self.observed_filenames)):
                    outfile.write(f"{filename}\n")
                info(
                    f"'{self.observed_filenames_outfile}' updated with "
                    f"{len(self.observed_filenames)} filenames"
                )


if __name__ == "__main__":
    DirectoryWatcher.main()
