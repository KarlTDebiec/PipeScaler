#!/usr/bin/env python
#   pipescaler/scripts/directory_watcher.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
from __future__ import annotations

import logging
import re
from argparse import ArgumentParser
from inspect import cleandoc
from logging import debug, info
from os import environ, makedirs, remove, rmdir
from os.path import basename, expandvars, isdir, isfile, normpath, splitext
from shutil import copy, move
from time import sleep
from typing import Any, Dict, List, Optional

import yaml

from pipescaler.common import (
    CLTool,
    DirectoryNotFoundError,
    validate_input_path,
    validate_output_path,
)
from pipescaler.core import parse_file_list


class DirectoryWatcher(CLTool):
    """"""

    exclusions = {".DS_Store", "desktop"}

    def __init__(
        self,
        copy_directory: str,
        input_directory: str,
        classified_directories: str,
        move_directory: str,
        rules: List[Dict[str, str]],
        observed_filenames_infile: Optional[str] = None,
        observed_filenames_outfile: Optional[str] = None,
        purge_directory: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initializes."""
        super().__init__(**kwargs)

        if self.verbosity == 1:
            logging.basicConfig(level=logging.WARNING)
        elif self.verbosity == 2:
            logging.basicConfig(level=logging.INFO)
        elif self.verbosity >= 3:
            logging.basicConfig(level=logging.DEBUG)

        # Input
        self.input_directory = validate_input_path(
            input_directory, file_ok=False, directory_ok=True
        )

        self.classified_filenames = parse_file_list(classified_directories)

        if purge_directory is not None:
            try:
                self.purge_directory = validate_input_path(
                    purge_directory, file_ok=False, directory_ok=True
                )
            except DirectoryNotFoundError:
                self.purge_directory = None
        else:
            self.purge_directory = None

        if observed_filenames_infile is not None:
            self.observed_filenames = parse_file_list(observed_filenames_infile)
        else:
            self.observed_filenames = set()

        if observed_filenames_outfile is not None:
            self.observed_filenames_outfile = validate_output_path(
                observed_filenames_outfile
            )
        else:
            self.observed_filenames_outfile = None

        # Operations
        self.rules = [{re.compile(next(iter(r))): r[next(iter(r))]} for r in rules]

        # Output
        self.copy_directory = validate_output_path(
            copy_directory, file_ok=False, directory_ok=True
        )
        self.move_directory = validate_output_path(
            move_directory, file_ok=False, directory_ok=True
        )

    def __call__(self, *args, **kwargs):

        # Prepare to run
        self.purge_copy_directory()
        self.purge_purge_directory()

        # Run on existing files
        self.process_existing_files_in_input_directory()
        self.write_observed_filenames_to_outfile()

        # Watch for new files
        self.watch_new_files_in_input_directory()

    def perform_operation_for_filename(self, filename):
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
                f"{self.input_directory}/{filename}.png",
                f"{self.copy_directory}/{filename}.png",
            )
            info(f"'{filename}' copied to '{self.copy_directory}'")
        elif status == "move":
            if not isdir(self.move_directory):
                makedirs(self.move_directory)
                info(f"'{self.move_directory}' created")
            move(
                f"{self.input_directory}/{filename}.png",
                f"{self.move_directory}/{filename}.png",
            )
            info(f"'{filename}' moved to '{self.move_directory}'")
        elif status == "remove":
            remove(f"{self.input_directory}/{filename}.png")
            info(f"'{filename}' deleted")
        else:
            raise ValueError()

    def process_existing_files_in_input_directory(self):
        filenames = parse_file_list(self.input_directory, False)
        filenames = list(filenames)
        filenames.sort(reverse=True)
        for filename in filenames:
            self.perform_operation_for_filename(filename)

    def purge_copy_directory(self):
        if isdir(self.copy_directory):
            for filename in parse_file_list(self.copy_directory, absolute_paths=True):
                remove(filename)

    def purge_purge_directory(self):
        if self.purge_directory is not None:
            purge_filenames = parse_file_list(self.purge_directory)
            for filename in purge_filenames:
                if isfile(f"{self.input_directory}/{filename}.png"):
                    remove(f"{self.input_directory}/{filename}.png")
                    info(f"'{filename}' purged")
                if isfile(f"{self.purge_directory}/{filename}.png"):
                    remove(f"{self.purge_directory}/{filename}.png")
                    info(f"'{filename}' removed from purge directory")
            rmdir(self.purge_directory)
            info(f"'{self.purge_directory}' removed")

    def select_operation_for_filename(self, filename):

        if filename in self.classified_filenames:
            return "known"

        for rule in self.rules:
            regex = next(iter(rule))
            action = rule[next(iter(rule))]
            if regex.match(filename):
                return action

        return "copy"

    def watch_new_files_in_input_directory(self):
        try:
            from watchdog.events import FileSystemEventHandler
            from watchdog.observers import Observer
        except ImportError as e:
            raise e

        class FileCreatedEventHandler(FileSystemEventHandler):
            def __init__(self, host) -> None:
                self.host = host

            def on_created(self, event):
                filename = splitext(basename(event.key[1]))[0]
                self.host.perform_operation_for_filename(filename)

        event_handler = FileCreatedEventHandler(self)
        observer = Observer()
        observer.schedule(event_handler, self.input_directory)
        observer.start()
        try:
            while True:
                sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    def write_observed_filenames_to_outfile(self):
        if self.observed_filenames_outfile is not None:
            with open(self.observed_filenames_outfile, "w") as outfile:
                for filename in sorted(list(self.observed_filenames)):
                    outfile.write(f"{filename}\n")
                print(
                    f"'{self.observed_filenames_outfile}' updated with "
                    f"{len(self.observed_filenames)} filenames"
                )

    @classmethod
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """
        Constructs argument parser.

        Args:
            kwargs (Any): Additional keyword arguments

        Returns:
            parser (ArgumentParser): Argument parser
        """
        description = kwargs.pop("description", cleandoc(cls.__doc__))
        parser = super().construct_argparser(description=description, **kwargs)

        # Input
        parser.add_argument(
            "conf_file", type=cls.input_path_arg(), help="configuration file"
        )

        return parser

    @classmethod
    def main(cls) -> None:
        """Parses arguments, constructs tool, and calls tool."""
        parser = cls.construct_argparser()
        kwargs = vars(parser.parse_args())

        conf_file = kwargs.pop("conf_file")
        with open(validate_input_path(conf_file), "r") as f:
            conf = yaml.load(f, Loader=yaml.SafeLoader)

        # Set environment variables
        for key, value in conf.pop("environment", {}).items():
            environ[key] = normpath(expandvars(value))

        tool = cls(**{**kwargs, **conf})
        tool()


if __name__ == "__main__":
    DirectoryWatcher.main()
