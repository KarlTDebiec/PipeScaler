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
from typing import Any, List, Optional, Set, Union

import numpy as np
import pandas as pd
from imagehash import average_hash, dhash, hex_to_hash, phash, whash
from PIL import Image
from scipy.stats import zscore

from pipescaler.common import (
    DirectoryNotFoundError,
    validate_input_directory,
    validate_output_directory,
    validate_output_file,
)
from pipescaler.core import ConfigurableCommandLineTool, get_files
from pipescaler.sorters import AlphaSorter, GrayscaleSorter

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
        hash_cache_file: Optional[str] = None,
        scaled_pairs_file: Optional[str] = None,
        scaled_pairs_image_directory: Optional[str] = None,
        purge_directory: Optional[str] = None,
        observed_filenames_infile: Optional[str] = None,
        observed_filenames_outfile: Optional[str] = None,
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
            ignore_directory: Directory or directories of reviewed images to skip
            hash_cache_file: CSV file to read/write cache of image hashes
            scaled_pairs_file: CSV file to read/write scaled image relationships
            scaled_pairs_image_directory: Directory to which to write concatenated
              scaled image pairs
            observed_filenames_infile: Text file from which to read list of observed
              files
            observed_filenames_outfile: Text file to which to write list of observed
              files
            purge_directory: Directory of reviewed images to purge from input
              directory or directories
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        def validate_input_directories(input_directories: Union[str, List[str]]):
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

        self.hash_cache_file = None
        """CSV file from which to read/write image hash cache"""
        if hash_cache_file is not None:
            self.hash_cache_file = validate_output_file(hash_cache_file)

        self.move_directory = validate_output_directory(move_directory)
        """Directory to which to move images that match 'move' rule"""

        self.purge_directory = None
        """Directory containing files which should be purged from input directories"""
        if purge_directory is not None:
            try:
                self.purge_directory = validate_input_directory(purge_directory)
            except DirectoryNotFoundError:
                self.purge_directory = None

        self.reviewed_directories = []
        """Directories containing files which have been reviewed"""
        if reviewed_directory is not None:
            self.reviewed_directories = validate_input_directories(reviewed_directory)

        self.scaled_pairs_file = None
        """CSV file from which to read/write scaled image pairs"""
        if scaled_pairs_file is not None:
            self.scaled_pairs_file = validate_output_file(scaled_pairs_file)

        self.scaled_pairs_image_directory = None
        """Directory to which images of scaled pairs should be written"""
        if scaled_pairs_image_directory is not None:
            self.scaled_pairs_image_directory = validate_output_directory(
                scaled_pairs_image_directory
            )

        self.observed_filenames = set()
        if observed_filenames_infile is not None:
            self.observed_filenames = get_files(observed_filenames_infile, style="base")
        self.observed_filenames_outfile = None
        """Text file to which to write observed filenames"""
        if observed_filenames_outfile is not None:
            self.observed_filenames_outfile = validate_output_file(
                observed_filenames_outfile
            )

        self.classified_filenames = get_files(self.reviewed_directories, style="base")
        """Base filenames of images in classified directories"""

        self.hashes = pd.DataFrame(
            {
                "filename": pd.Series(dtype="str"),
                "scale": pd.Series(dtype="float"),
                "width": pd.Series(dtype="int"),
                "height": pd.Series(dtype="int"),
                "mode": pd.Series(dtype="str"),
                "average hash": pd.Series(dtype="str"),
                "difference hash": pd.Series(dtype="str"),
                "perceptual hash": pd.Series(dtype="str"),
                "wavelet hash": pd.Series(dtype="str"),
            }
        )
        """Image hashes"""
        if self.hash_cache_file is not None and isfile(self.hash_cache_file):
            self._hashes = pd.read_csv(self.hash_cache_file)
            info(f"Image hashes read from '{self.hash_cache_file}'")

        self.ignore_filenames = get_files(self.ignore_directories, style="base")
        """Base filenames of images to ignore"""

        self.rules = [(re.compile(regex), action) for regex, action in rules]
        """Rules by which to classify images"""

        self.scaled_pairs = pd.DataFrame(
            {
                "filename": pd.Series(dtype="str"),
                "scale": pd.Series(dtype="float"),
                "scaled filename": pd.Series(dtype="str"),
            }
        )
        """Scaled image pairs"""
        if self.scaled_pairs_file is not None and isfile(self.scaled_pairs_file):
            self.scaled_pairs = pd.read_csv(self.scaled_pairs_file)
            info(f"Scaled image pairs read from '{self.scaled_pairs_file}'")

        absolute_filenames = get_files(self.input_directories, style="absolute")
        absolute_filenames = sorted(list(absolute_filenames))
        self.filenames = {splitext(basename(f))[0]: f for f in absolute_filenames}
        """Input filenames; keys are base names and values are absolute paths"""

        self.alpha_sorter = AlphaSorter()
        """Alpha sorter"""

        self.grayscale_sorter = GrayscaleSorter()
        """Grayscale sorter"""

    def __call__(self, **kwargs: Any) -> Any:
        """
        Perform operations

        Arguments:
            **kwargs: Additional keyword arguments
        """

        # Prepare to run
        self.purge_copy_directory()
        self.purge_purge_directory()

        # Run on existing files
        self.hash_images_in_input_directory()
        for parent in self.scaled_parent_filenames:
            self.save_scaled_debug_image(parent)
        self.identify_scaled_images()
        # self.process_existing_files_in_input_directory()
        # self.write_observed_filenames_to_outfile()

        # Watch for new files
        # self.watch_new_files_in_input_directory()

    @property
    def scaled_child_filenames(self) -> Set[str]:
        """Child images"""
        return set(self.scaled_pairs["scaled filename"])

    @property
    def scaled_parent_filenames(self) -> Set[str]:
        """Parent images"""
        return set(self.scaled_pairs["filename"])

    def hash_images_in_input_directory(self):
        """Hash images in input directory"""
        # TODO: Somehow handle images that should be skipped
        # TODO: Handle known images as well
        image_hashes_changed = False
        hashed_filenames = set(self.hashes["filename"])

        for base_filename in self.filenames.keys():
            if base_filename not in hashed_filenames:
                self.hashes = self.hashes.append(self.hash_image(base_filename))
                hashed_filenames.add(base_filename)
                image_hashes_changed = True

        if image_hashes_changed:
            self.hashes = self.hashes.reset_index(drop=True)
            self.hashes.to_csv(self.hash_cache_file, index=False)
            info(f"Image hashes saved to '{self.hash_cache_file}'")

    def hash_image(self, filename: str) -> pd.DataFrame:
        """Hash an image"""
        absolute_filename = self.filenames[filename]
        scale = 1.0
        scaled_image = image = Image.open(absolute_filename)
        scaled_size = original_size = image.size
        if self.grayscale_sorter(absolute_filename) == "keep_rgb":
            mode = "RGB"
        else:
            mode = "L"
        if self.alpha_sorter(absolute_filename) == "keep_alpha":
            mode += "A"
        rows = []
        while True:
            rows.append(
                {
                    "filename": filename,
                    "scale": scale,
                    "width": scaled_size[0],
                    "height": scaled_size[1],
                    "mode": mode,
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

        return pd.DataFrame(rows)

    def get_candidate_children(
        self, parent: pd.Series, width: int, height: int
    ) -> pd.DataFrame:
        """Get candidate children of parent"""
        # Select potential child images
        candidate_children = self.hashes.loc[
            (self.hashes["scale"] == 1.0)
            & (self.hashes["width"] == width)
            & (self.hashes["height"] == height)
            & (self.hashes["mode"] == parent["mode"])
            & ~(self.hashes["filename"].isin(self.scaled_parent_filenames))
            & ~(self.hashes["filename"].isin(self.scaled_child_filenames))
            & ~(self.hashes["filename"].isin(self.ignore_filenames))
        ].copy(deep=True)

        # Score potential child images
        if len(candidate_children) > 0:
            hash_types = ["average", "difference", "perceptual", "wavelet"]
            for hash_type in hash_types:
                candidate_children[f"{hash_type} hamming"] = candidate_children.apply(
                    lambda child: self.hamming_distance(parent, child, hash_type),
                    axis=1,
                )
            candidate_children["hamming sum"] = candidate_children[
                [f"{hash_type} hamming" for hash_type in hash_types]
            ].sum(axis=1)
            candidate_children["hamming sum z score"] = zscore(
                candidate_children["hamming sum"]
            )

        return candidate_children

    def identify_scaled_images(self):
        """Identify scaled images"""
        # Loop over potential parent images starting from the largest
        parents = self.hashes.loc[
            (self.hashes["scale"] == 1.0)
            & ~(self.hashes["filename"].isin(self.scaled_parent_filenames))
            & ~(self.hashes["filename"].isin(self.scaled_child_filenames))
            & ~(self.hashes["filename"].isin(self.ignore_filenames))
        ].sort_values(["width", "height", "filename"], ascending=False)
        for _, parent in parents.iterrows():
            # Skip potential parents that are now known to be children
            if parent["filename"] in self.scaled_child_filenames:
                continue

            print(parent)
            scale = 0.5
            debug_rows = []
            new_pairs = []
            while True:
                width = round(parent["width"] * scale)
                height = round(parent["height"] * scale)
                if min(width, height) < 8:
                    break

                # Prepare candidate children
                candidate_children = self.get_candidate_children(parent, width, height)

                # Accept or reject best candidate
                if len(candidate_children) > 0:
                    candidate_child = self.get_best_candidate_child(candidate_children)
                    accept_child = candidate_child["hamming sum"] <= 75
                    if accept_child and len(candidate_children) >= 5:
                        accept_child = candidate_child["hamming sum z score"] < -1
                    debug_rows.append(
                        {
                            "filename": parent["filename"],
                            "scale": scale,
                            "scaled filename": candidate_child["filename"],
                            "candidates": len(candidate_children),
                            "hamming sum": candidate_child["hamming sum"],
                            "z score": candidate_child["hamming sum z score"],
                            "z score margin": candidate_child[
                                "hamming sum z score margin"
                            ],
                            "accept": accept_child,
                        }
                    )
                    if accept_child:
                        new_pairs.append(
                            {
                                "filename": parent["filename"],
                                "scale": scale,
                                "scaled filename": candidate_child["filename"],
                            }
                        )

                # Move on to next scale
                scale /= 2.0

            # Print debug output
            if len(debug_rows) > 0:
                debug_rows = pd.DataFrame(debug_rows)
                print(debug_rows)
                self.concatenate_images(
                    *[parent["filename"]] + list(debug_rows["scaled filename"])
                ).show()
                print()

            # Update image sets
            if len(new_pairs) > 0:
                new_pairs = pd.DataFrame(new_pairs)
                self.scaled_pairs = self.scaled_pairs.append(new_pairs)
                self.scaled_pairs.sort_values(["filename", "scale"])
                # noinspection PyTypeChecker
                self.scaled_pairs.to_csv(self.scaled_pairs, index=False)
                info(f"Scaled images saved to '{self.scaled_pairs}'")
                self.save_scaled_debug_image(parent["filename"])

    def save_scaled_debug_image(self, parent):
        children = self.scaled_pairs.loc[
            self.scaled_pairs["filename"] == parent, "scaled filename"
        ]
        debug_image = self.concatenate_images(parent, *children)
        debug_outfile = join(self.scaled_pairs_image_directory, f"{parent}.png")
        debug_image.save(debug_outfile)
        info(f"Scaled image saved to '{debug_outfile}'")

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

    def process_existing_files_in_input_directory(self):
        """Process existing files in input directory"""
        for filename in self.filenames:
            self.perform_operation_for_filename(filename)

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
            purge_filenames = get_files(self.purge_directory, style="full")
            for filename in purge_filenames:
                for input_directory in self.input_directories:
                    if isfile(join(input_directory, filename)):
                        remove(join(input_directory, filename))
                        info(
                            f"'{filename}' removed from input directory "
                            f"'{input_directory}'"
                        )
                if isfile(join(self.purge_directory, filename)):
                    remove(join(self.purge_directory, filename))
                    info(f"'{filename}' removed from purge directory")
            rmdir(self.purge_directory)
            info(f"'{self.purge_directory}' removed")

    def select_operation_for_filename(self, filename):
        """Select operation for filename"""

        if filename in self.classified_filenames:
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

    def concatenate_images(self, *filenames: str) -> Image.Image:
        """Concatenate images"""
        images = []
        size = None
        for filename in filenames:
            image = Image.open(self.filenames[filename])

            if size is None:
                size = image.size

            images.append(image)

        concatenated = Image.new("RGBA", (size[0] * len(images), size[1]))
        for i, image in enumerate(images):
            if image.size == size:
                concatenated.paste(image, (size[0] * i, 0))
            else:
                concatenated.paste(
                    image.resize(size, resample=Image.NEAREST), (size[0] * i, 0)
                )
        return concatenated

    @staticmethod
    def get_best_candidate_child(candidates: pd.DataFrame) -> pd.Series:
        """Get best candidate child"""
        if len(candidates) > 1:
            top_two = candidates["hamming sum z score"].nsmallest(2)
            best = candidates.loc[top_two.index[0]].copy(deep=True)
            best["hamming sum z score margin"] = top_two.iloc[0] - top_two.iloc[1]
        else:
            best = candidates.iloc[0].copy(deep=True)
            best["hamming sum z score margin"] = np.nan

        return best

    @staticmethod
    def hamming_distance(parent: pd.Series, child: pd.Series, hash_type: str) -> int:
        """Calculate hamming distance"""
        parent_hash = hex_to_hash(parent[f"{hash_type} hash"])
        child_hash = hex_to_hash(child[f"{hash_type} hash"])
        return parent_hash - child_hash


if __name__ == "__main__":
    DirectoryWatcher.main()
