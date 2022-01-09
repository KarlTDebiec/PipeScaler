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
        remove_directory: Optional[str] = None,
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

        self.hash_cache_file = None
        """CSV file from which to read/write image hash cache"""
        if hash_cache_file is not None:
            self.hash_cache_file = validate_output_file(hash_cache_file)

        self.move_directory = validate_output_directory(move_directory)
        """Directory to which to move images that match 'move' rule"""

        self.remove_directory = None
        """Directory containing files which should be removed from input directories"""
        if remove_directory is not None:
            try:
                self.remove_directory = validate_input_directory(remove_directory)
            except DirectoryNotFoundError:
                self.remove_directory = None

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
            self.hashes = pd.read_csv(self.hash_cache_file)
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
        info(f"Found {len(self.filenames)} infiles in {self.input_directories}")

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
        self.remove_files_in_copy_directory()
        self.remove_files_in_remove_directory()

        # Run on existing files
        self.hash_images_in_input_directory()
        # for parent in self.scaled_parent_filenames:
        #     self.save_scaled_pairs_image(parent)
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

        for base_filename in self.filenames:
            if base_filename in self.ignore_filenames:
                continue
            if base_filename not in hashed_filenames:
                self.hashes = self.hashes.append(self.get_hash(base_filename))
                hashed_filenames.add(base_filename)
                image_hashes_changed = True

        if image_hashes_changed:
            self.hashes = self.hashes.reset_index(drop=True)
            self.hashes.to_csv(self.hash_cache_file, index=False)
            info(f"Image hashes saved to '{self.hash_cache_file}'")

    def get_hash(self, filename: str) -> pd.DataFrame:
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

    def get_candidate_children_hashes(
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

    def get_known_children(self, parent: pd.Series) -> pd.DataFrame:
        return self.scaled_pairs.loc[
            self.scaled_pairs["filename"] == parent["filename"]
        ]

    def get_candidate_parent_hashes(self) -> pd.DataFrame:
        return self.hashes.loc[
            (self.hashes["scale"] == 1.0)
            & ~(self.hashes["filename"].isin(self.scaled_child_filenames))
            & ~(self.hashes["filename"].isin(self.ignore_filenames))
        ].sort_values(["width", "height", "filename"], ascending=False)

    def search_for_pair(
        self, parent: pd.Series, scale: float, width: int, height: int
    ) -> Optional[pd.DataFrame]:
        candidate_children = self.get_candidate_children_hashes(parent, width, height)

        if len(candidate_children) == 0:
            return

        candidate_child = self.get_best_candidate_child(candidate_children)
        accept_child = candidate_child["hamming sum"] <= 75
        if accept_child and len(candidate_children) >= 5:
            accept_child = candidate_child["hamming sum z score"] < -1
        if accept_child:
            info(candidate_child)
            return {
                "filename": parent["filename"],
                "scale": scale,
                "scaled filename": candidate_child["filename"],
            }

    def identify_scaled_images(self):
        """Identify scaled images"""
        # Loop over potential parent images starting from the largest
        for _, parent in self.get_candidate_parent_hashes().iterrows():
            # Skip potential parents that are now known to be children
            if parent["filename"] in self.scaled_child_filenames:
                continue

            info(f"Searching for scaled child images of '{parent['filename']}'")
            known_pairs = self.get_known_children(parent)
            scale = 0.5
            new_pairs = []
            while True:
                width = round(parent["width"] * scale)
                height = round(parent["height"] * scale)
                if min(width, height) < 8:
                    break
                if scale not in known_pairs["scale"].values:
                    new_pair = self.search_for_pair(parent, scale, width, height)
                    if new_pair is not None:
                        new_pairs.append(new_pair)

                # Move on to next scale
                scale /= 2.0

            # Update image sets
            if len(new_pairs) > 0:
                new_pairs = pd.DataFrame(new_pairs)
                info(
                    f"To known pairs:\n{known_pairs}\n"
                    f"have been added new pairs:\n{new_pairs}"
                )
                all_pairs = known_pairs.append(new_pairs)
                all_pairs = all_pairs.sort_values("scale", ascending=False)
                children = list(all_pairs["scaled filename"])
                self.concatenate_images(parent["filename"], *children).show()
                prompt = f"Confirm ({'y' * len(new_pairs)}/{'n' * len(new_pairs)})?: "
                regex = re.compile(f"^[yn]{{{len(new_pairs)}}}$", re.IGNORECASE)
                response = input(prompt).lower()
                if regex.match(response):
                    scaled_pairs_modified = False
                    for i in range(len(new_pairs)):
                        if response[i] == "y":
                            self.scaled_pairs = self.scaled_pairs.append(
                                new_pairs.iloc[i]
                            )
                            scaled_pairs_modified = True
                            info(f"{new_pairs.iloc[i]} accepted")
                    if scaled_pairs_modified:
                        self.scaled_pairs = self.scaled_pairs.sort_values(
                            ["filename", "scale"], ascending=False
                        )
                        self.scaled_pairs.to_csv(self.scaled_pairs_file, index=False)
                        info(f"Scaled pairs saved to '{self.scaled_pairs_file}'")
            self.save_scaled_pairs_image(parent["filename"])

    def save_scaled_pairs_image(self, parent):
        """Save scaled debug image"""
        children = self.scaled_pairs.loc[
            self.scaled_pairs["filename"] == parent, "scaled filename"
        ]
        if len(children) > 0:
            image = self.concatenate_images(parent, *children)
            outfile = join(self.scaled_pairs_image_directory, f"{parent}.png")
            image.save(outfile)
            info(f"Scaled image saved to '{outfile}'")

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
    def get_best_candidate_child(candidate_children: pd.DataFrame) -> pd.Series:
        """Get best candidate child"""
        if len(candidate_children) > 1:
            top_two = candidate_children["hamming sum z score"].nsmallest(2)
            best = candidate_children.loc[top_two.index[0]].copy(deep=True)
            best["hamming sum z score margin"] = top_two.iloc[0] - top_two.iloc[1]
        else:
            best = candidate_children.iloc[0].copy(deep=True)
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
