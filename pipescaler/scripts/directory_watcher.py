#!/usr/bin/env python
#   pipescaler/scripts/directory_watcher.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
""""""
from __future__ import annotations

import re
from argparse import ArgumentParser
from inspect import cleandoc
from logging import debug, info
from os import environ, makedirs, remove, rmdir
from os.path import basename, expandvars, isdir, isfile, normpath, splitext
from shutil import copy, move
from time import sleep
from typing import Any, Dict, List, Optional

import pandas as pd
from imagehash import average_hash, dhash, phash, whash
from PIL import Image

from pipescaler.common import (
    CLTool,
    DirectoryNotFoundError,
    validate_input_path,
    validate_output_path,
)
from pipescaler.core import get_files
from pipescaler.core.file import read_yaml

pd.set_option("display.max_rows", None, "display.max_columns", None)


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
        hash_cache: Optional[str] = None,
        observed_filenames_infile: Optional[str] = None,
        observed_filenames_outfile: Optional[str] = None,
        purge_directory: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initializes."""
        super().__init__(**kwargs)

        # Input
        self.input_directory = validate_input_path(
            input_directory, file_ok=False, directory_ok=True
        )

        self.classified_filenames = get_files(classified_directories)

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
            self.observed_filenames = get_files(observed_filenames_infile)
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

        if hash_cache is not None:
            try:
                self.hash_cache = validate_input_path(hash_cache)
                self.image_hashes = pd.read_hdf(self.hash_cache)
            except (FileNotFoundError):
                self.hash_cache = validate_output_path(hash_cache)
                self.image_hashes = pd.DataFrame(
                    {
                        "filename": pd.Series(dtype="str"),
                        "scale": pd.Series(dtype="float"),
                        "width": pd.Series(dtype="int"),
                        "height": pd.Series(dtype="int"),
                        "average hash": pd.Series(dtype="str"),
                        "difference hash": pd.Series(dtype="str"),
                        "perceptual hash": pd.Series(dtype="str"),
                        "wavelet hash": pd.Series(dtype="str"),
                    }
                )
                self.image_hashes = self.image_hashes.set_index(["filename", "scale"])
        else:
            self.image_hashes = pd.DataFrame(
                {
                    "filename": pd.Series(dtype="str"),
                    "scale": pd.Series(dtype="float"),
                    "width": pd.Series(dtype="int"),
                    "height": pd.Series(dtype="int"),
                    "average hash": pd.Series(dtype="str"),
                    "difference hash": pd.Series(dtype="str"),
                    "perceptual hash": pd.Series(dtype="str"),
                    "wavelet hash": pd.Series(dtype="str"),
                }
            )
            self.image_hashes = self.image_hashes.set_index(["filename", "scale"])

        self.image_sets = {}
        # self.image_sets = {"filename": {0.5: "filename"}}
        # filename original_size scale scaled_size filename

    def __call__(self, **kwargs: Any) -> Any:
        """
        Perform operations

        Args:
            **kwargs: Additional keyword arguments
        """

        # Prepare to run
        self.purge_copy_directory()
        self.purge_purge_directory()

        # Run on existing files
        self.process_existing_files_in_input_directory()
        # self.write_observed_filenames_to_outfile()

        # Watch for new files
        # self.watch_new_files_in_input_directory()

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
        filenames = list(get_files(self.input_directory, style="absolute"))
        filenames.sort(reverse=False)
        for filename in filenames:
            base_filename = splitext(basename(filename))[0]
            print(base_filename, self.image_hashes.size)
            if not self.image_hashes.index.isin([(base_filename, 1.0)]).any():
                self.store_hashes(filename)
            # self.perform_operation_for_filename(base_filename)
        self.image_hashes.to_hdf(self.hash_cache, "image_hashes")

    def purge_copy_directory(self):
        """
        Remove existing files in the copy directory; which is refreshed from the input
        directory with each run
        """
        if isdir(self.copy_directory):
            for filename in get_files(self.copy_directory, style="absolute"):
                remove(filename)

    def purge_purge_directory(self):
        """
        Remove existing files in the purge directory, as well as their source files in
        the input directory; afterwards remove the purge directory itself
        """
        if self.purge_directory is not None:
            purge_filenames = get_files(self.purge_directory)
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

    def store_hashes(self, filename: str) -> None:
        scale = 1.0
        scaled_image = image = Image.open(filename)
        scaled_size = original_size = image.size
        rows = []
        while True:
            rows.append(
                {
                    "filename": splitext(basename(filename))[0],
                    "scale": scale,
                    "width": scaled_size[0],
                    "height": scaled_size[1],
                    "average hash": str(average_hash(scaled_image)),
                    "difference hash": str(dhash(scaled_image)),
                    "perceptual hash": str(phash(scaled_image)),
                    "wavelet hash": str(whash(scaled_image)),
                }
            )
            scale /= 2.0
            scaled_size = (
                round(original_size[0] * scale),
                round(original_size[1] * scale),
            )
            if min(scaled_size) < 8:
                break
            scaled_image = image.resize(scaled_size, Image.NEAREST)
        self.image_hashes = self.image_hashes.append(
            pd.DataFrame(rows).set_index(["filename", "scale"])
        )

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
        Construct argument parser

        Arguments:
            **kwargs: Additional keyword arguments

        Returns:
            Argument parser
        """
        description = kwargs.pop(
            "description", cleandoc(cls.__doc__) if cls.__doc__ is not None else ""
        )
        parser = super().construct_argparser(description=description, **kwargs)

        # Input
        parser.add_argument(
            "conf_file", type=cls.input_path_arg(), help="configuration file"
        )

        return parser

    @classmethod
    def main(cls) -> None:
        """Parse arguments, construct tool, and call tool"""
        parser = cls.construct_argparser()
        kwargs = vars(parser.parse_args())

        conf = read_yaml(kwargs.pop("conf_file"))

        # Set environment variables
        for key, value in conf.pop("environment", {}).items():
            environ[key] = normpath(expandvars(value))

        tool = cls(**{**kwargs, **conf})
        tool()


if __name__ == "__main__":
    DirectoryWatcher.main()
