#!/usr/bin/env python
#   pipescaler/scripts/directoryw_watcher.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
""""""
####################################### MODULES ########################################
from __future__ import annotations

import logging
import re
from argparse import ArgumentParser
from os import remove
from os.path import basename, isfile, splitext
from shutil import copy, move
from time import sleep
from typing import Any, Dict, List
from logging import debug, info
import yaml

from pipescaler.common import (
    CLTool,
    validate_input_path,
    validate_output_path,
)
from pipescaler.core import parse_file_list


####################################### CLASSES ########################################
class DirectoryWatcher(CLTool):
    exclusions = {".DS_Store", "desktop"}

    # region Builtins

    def __init__(
        self,
        copy_directory: str,
        input_directory: str,
        known_directory: str,
        known_filenames_list: str,
        move_directory: str,
        purge_directory: str,
        rules: List[Dict[str, str]],
        **kwargs: Any,
    ) -> None:
        """
        Initializes.

        Args:
            conf_file (str): file from which to load configuration
        """
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
        self.known_filenames = parse_file_list(known_directory)
        self.known_filenames_file = validate_input_path(known_filenames_list)
        purge_filenames = parse_file_list(purge_directory)
        for filename in purge_filenames:
            if isfile(f"{self.input_directory}/{filename}.png"):
                remove(f"{self.input_directory}/{filename}.png")
                info(f"'{filename}' purged")
            if isfile(f"{purge_directory}/{filename}.png"):
                remove(f"{purge_directory}/{filename}.png")
                info(f"'{filename}' removed from purge directory")

        # Operations
        self.rules = [{re.compile(next(iter(r))): r[next(iter(r))]} for r in rules]

        # Output
        self.copy_directory = validate_output_path(
            copy_directory, file_ok=False, directory_ok=True
        )
        for filename in parse_file_list(self.copy_directory, full_paths=True):
            remove(filename)
        self.move_directory = validate_output_path(
            move_directory, file_ok=False, directory_ok=True
        )

    def __call__(self, *args, **kwargs):
        filenames = parse_file_list(self.input_directory, False)
        filenames = list(filenames)
        filenames.sort(key=self.sort, reverse=True)
        for filename in filenames:
            self.process_file(filename)

        known_filenames = parse_file_list(self.known_filenames_file)
        known_filenames |= parse_file_list(self.input_directory, False)
        with open(self.known_filenames_file, "w") as outfile:
            for filename in sorted(list(known_filenames)):
                if self.check_file(filename) in ("known", "copy"):
                    outfile.write(f"{filename}\n")
            print(f"'{self.known_filenames_file}' updated")

        self.watch_dump_directory()

    def check_file(self, filename):

        if filename in self.known_filenames:
            return "known"

        for rule in self.rules:
            regex = next(iter(rule))
            action = rule[next(iter(rule))]
            if regex.match(filename):
                return action

        return "copy"

    def process_file(self, filename):
        status = self.check_file(filename)
        if status == "known":
            debug(f"'{filename}' known")
        elif status == "ignore":
            debug(f"'{filename}' ignored")
        elif status == "copy":
            copy(
                f"{self.input_directory}/{filename}.png",
                f"{self.copy_directory}/{filename}.png",
            )
            info(f"'{filename}' copied to '{self.copy_directory}'")
        elif status == "move":
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

    def watch_dump_directory(self):
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
                self.host.process_file(filename)

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

    # endregion

    # region Class Methods

    @classmethod
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """
        Constructs argument parser.

        Returns:
            ArgumentParser: Argument parser
        """
        description = kwargs.get("description", __doc__.strip())
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

        tool = cls(**{**kwargs, **conf})
        tool()

    # endregion

    @staticmethod
    def sort(filename):
        components = splitext(basename(filename))[0].split("_")
        if len(components) == 4:
            size = components[1]
            code = components[2]
        elif len(components) == 5:
            size = components[1]
            code = components[3]
        elif len(components) == 6:
            size = components[1]
            code = components[3]
        else:
            raise ValueError()
        width, height = size.split("x")
        return int(f"1{int(width):04d}{int(height):04d}{int(code, 16):022d}")


######################################### MAIN #########################################
if __name__ == "__main__":
    DirectoryWatcher.main()
