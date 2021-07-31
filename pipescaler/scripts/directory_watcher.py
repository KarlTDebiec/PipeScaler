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
from os.path import basename, splitext
from shutil import copy, move
from time import sleep
from typing import Any, Dict, List

import yaml
from IPython import embed

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

    def __init__(self,
                 copy_directory: str,
                 input_directory: str,
                 known_directory: str,
                 move_directory: str,
                 rules: List[Dict[str,str]],
                 **kwargs: Any) -> None:
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
        self.input_directory = validate_input_path(input_directory,
                                                   file_ok=False, directory_ok=True)
        self.known_filenames = parse_file_list(known_directory)

        # Operations
        self.rules = [{re.compile(next(iter(r))): r[next(iter(r))]} for r in rules]

        # Output
        self.copy_directory = validate_output_path(copy_directory,
                                                     file_ok=False, directory_ok=True)
        for filename in parse_file_list(self.copy_directory, full_paths=True):
            remove(filename)
        self.move_directory = validate_output_path(move_directory,
                                                   file_ok=False, directory_ok=True)

    def __call__(self, *args, **kwargs):
        filenames = parse_file_list(self.input_directory, False)
        filenames = list(filenames)
        filenames.sort(key=self.sort, reverse=True)
        for filename in filenames:
            self.review_file(filename)

        self.watch_dump_directory()

    def review_file(self, filename):

        if filename in self.known_filenames:
            # print(f"'{filename}' known")
            return

        for rule in self.rules:
            regex = next(iter(rule))
            action = rule[next(iter(rule))]
            if regex.match(filename):
                if action == "ignore":
                    print(f"'{filename}' ignored")
                    return
                elif action == "copy":
                    print(f"'{filename}' copied to '{self.copy_directory}'")
                    copy(f"{self.input_directory}/{filename}.png", f"{self.copy_directory}/{filename}.png")
                    return
                elif action == "move":
                    move(f"{self.input_directory}/{filename}.png", f"{self.move_directory}/{filename}.png")
                    print(f"'{filename}' moved to '{self.move_directory}'")
                    return
                elif action == "remove":
                    remove(f"{self.input_directory}/{filename}.png")
                    print(f"'{filename}' deleted")
                    return

        print(f"'{filename}' copied to '{self.copy_directory}'")
        copy(f"{self.input_directory}/{filename}.png", f"{self.copy_directory}/{filename}.png")
        return

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
                self.host.review_file(filename)

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
