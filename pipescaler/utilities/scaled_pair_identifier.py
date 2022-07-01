#!/usr/bin/env python
#  Copyright (C) 2020-2022. Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Identifies pairs of images in which one is rescaled from another."""
import re
from itertools import chain
from logging import info
from pathlib import Path
from typing import Iterable, Union

import numpy as np
import pandas as pd
from imagehash import average_hash, colorhash, dhash, phash, whash
from PIL import Image

from pipescaler.common import validate_input_directories, validate_input_directory
from pipescaler.core import Utility
from pipescaler.core.image import hstack_images, label_image, vstack_images
from pipescaler.core.image_hash_collection import ImageHashCollection
from pipescaler.core.image_pair_scorer import ImagePairScorer
from pipescaler.core.image_pairs_collection import ImagePairsCollection
from pipescaler.pipelines.sorters import AlphaSorter, GrayscaleSorter

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 0)


class ScaledPairIdentifier(Utility):
    """Identifies pairs of images in which one is rescaled from another."""

    hash_types = {
        "average": average_hash,
        "color": colorhash,
        "difference": dhash,
        "perceptual": phash,
        "wavelet": whash,
    }

    def __init__(
        self,
        input_directories: Union[Union[str, Path], Iterable[Union[str, Path]]],
        project_root: Union[str, Path],
        *,
        pairs_file: Union[str, Path] = "pairs.csv",
        hash_file: Union[str, Path] = "hashes.csv",
        interactive: bool = True,
    ):
        """Validate configuration and initialize.

        Arguments:
            input_directories: Directory or directories from which to read input files
            project_root: Root directory of project
            pairs_file: CSV file to read/write scaled image pairs
            hash_file: CSV file to read/write cache of image hashes
            interactive: Whether to prompt for interactive review
        """
        # Store input and output paths
        self.input_directories = validate_input_directories(input_directories)
        """Directories from which to read input files."""

        project_root = validate_input_directory(project_root)
        self.scaled_directory = project_root.joinpath("scaled")
        """Directory to which to move scaled images."""
        self.comparison_directory = project_root.joinpath("scaled_images")
        """Directory to which to write stacked scaled image sets."""

        # Prepare data structures
        self.hash_collection = ImageHashCollection(
            list(
                chain.from_iterable(
                    d.iterdir()
                    for d in self.input_directories + [self.scaled_directory]
                )
            ),
            hash_file,
        )
        """Image hashes."""
        self.pair_collection = ImagePairsCollection(pairs_file)
        """Image pairs."""
        self.pair_scorer = ImagePairScorer(self.hash_collection)
        """Image pair scorer."""

        self.interactive = interactive
        """Whether to prompt for interactive review."""

        # Prepare image sorters for image analysis
        self.alpha_sorter = AlphaSorter()
        """Alpha sorter."""
        self.grayscale_sorter = GrayscaleSorter()
        """Grayscale sorter."""

    @property
    def potential_parents(self) -> list[str]:
        full_size = self.hash_collection.full_size
        full_size_potential_parents = full_size.loc[
            ~(full_size["name"].isin(self.pair_collection.children))
        ]
        sorted_full_size_potential_parents = full_size_potential_parents.sort_values(
            ["width", "height", "name"], ascending=False
        )
        return sorted_full_size_potential_parents["name"]

    def identify_pairs(self):
        """Identify pairs."""
        for parent in self.potential_parents:
            # Known children may change as parents are reviewed
            if parent in self.pair_collection.children:
                continue

            print(f"Searching for children of {parent}")
            known_scores = self.pair_scorer.get_pair_scores(
                self.pair_collection[parent]
            )
            new_scores = []
            for scale in np.array([1 / (2**x) for x in range(1, 7)]):
                if "scale" in known_scores and scale in known_scores["scale"].values:
                    continue
                parent_hash = self.hash_collection[parent, 1.0].iloc[0]
                if round(parent_hash["width"] * scale) < 8:
                    break
                if round(parent_hash["height"] * scale) < 8:
                    break
                child_score = self.pair_scorer.get_best_child(parent, scale)
                if child_score is None:
                    break
                new_scores.append(child_score)

            # Update image sets
            if len(known_scores) > 0:
                print("KNOWN")
                print(known_scores)
            if len(new_scores) > 0:
                new_scores = pd.DataFrame(new_scores)
                print("NEW")
                print(new_scores)
                # result = self.review_candidate_pairs(known_pairs, new_pairs, new_scores)
                # if result == 0:
                #     break

    def review_candidate_pairs(
        self,
        known_pairs: pd.DataFrame,
        new_pairs: pd.DataFrame,
        new_pair_scores: pd.DataFrame,
    ) -> int:
        """Review candidate pairs of parent image.

        Arguments:
            known_pairs: Known pairs of parent
            new_pairs: Proposed new pairs of parent
            new_pair_scores: Scores of new pairs
        Returns:
        """
        info(
            f"To known pairs:\n"
            f"{known_pairs}\n"
            f"may be added new pairs:\n"
            f"{new_pairs}\n"
            f"with scores:\n"
            f"{new_pair_scores}"
        )
        all_pairs = known_pairs.append(new_pairs).sort_values("scale", ascending=False)
        parent = all_pairs.iloc[0]["filename"]
        children = list(all_pairs["scaled filename"])

        if self.interactive:
            self.get_stacked_image([parent, *children]).show()
        prompt = f"Confirm ({'y' * len(new_pairs)}/{'n' * len(new_pairs)})?: "
        accept_re = re.compile(f"^[yn]{{{len(new_pairs)}}}$", re.IGNORECASE)
        quit_re = re.compile("quit", re.IGNORECASE)
        if self.interactive:
            response = input(prompt).lower()
        else:
            response = "y" * len(new_pairs)
        if accept_re.match(response):
            scaled_pairs_modified = False
            for i in range(len(new_pairs)):
                if response[i] == "y":
                    self.pair_collection = self.pair_collection.append(
                        new_pairs.iloc[i]
                    )
                    scaled_pairs_modified = True
                    info(f"{new_pairs.iloc[i]} accepted")
            if scaled_pairs_modified:
                self.pair_collection = self.pair_collection.sort_values(
                    ["filename", "scale"], ascending=False
                )
                self.pair_collection.to_csv(self.pairs_file, index=False)
                info(f"Scaled pairs saved to '{self.pairs_file}'")
            return 1
        elif quit_re.match(response):
            return 0

    def get_pair_score_image(self, pair_scores) -> Image.Image:
        """Gets a concatenated image of images in pair_scores.

        Arguments:
            pair_scores: Pair scores
        Returns:
            Concatenated image of images in *pair_scores*
        """
        parent = pair_scores["filename"].values[0]
        children = list(pair_scores["scaled filename"].values)
        scores = list(pair_scores["hamming sum"].values)

        parent_image = Image.open(self.filenames[parent])
        if self.alpha_sorter(self.filenames[parent]) == "keep_alpha":
            # noinspection PyTypeChecker
            parent_array = np.array(parent_image)
            parent_color_image = Image.fromarray(np.squeeze(parent_array[:, :, :-1]))
            parent_alpha_image = Image.fromarray(parent_array[:, :, -1])
            child_color_images = []
            child_alpha_images = []

            for child, score in zip(children, scores):
                child_image = Image.open(self.filenames[child])
                # noinspection PyTypeChecker
                child_array = np.array(child_image)

                child_color_image = Image.fromarray(np.squeeze(child_array[:, :, :-1]))
                child_color_image = child_color_image.resize(
                    parent_image.size, Image.NEAREST
                )
                child_color_image = label_image(child_color_image, str(score))
                child_color_images.append(child_color_image)

                child_alpha_image = Image.fromarray(child_array[:, :, -1])
                child_alpha_image = child_alpha_image.resize(
                    parent_image.size, Image.NEAREST
                )
                child_alpha_images.append(child_alpha_image)

            color_image = hstack_images(parent_color_image, *child_color_images)
            alpha_image = hstack_images(parent_alpha_image, *child_alpha_images)
            return vstack_images(color_image, alpha_image)
        else:
            child_images = []
            for child, score in zip(children, scores):
                child_image = Image.open(self.filenames[child])
                child_image = child_image.resize(parent_image.size, Image.NEAREST)
                child_image = label_image(child_image, str(score))
                child_images.append(child_image)

            return hstack_images(parent_image, *child_images)

    def get_stacked_image(self, filenames: list[str]) -> Image.Image:
        """Get stacked images, rescaled to match first image, if necessary.

        Arguments:
            filenames: Basenames of files to stack
        Returns:s
            Stacked images, rescaled to match first image, if necessary
        """
        if self.alpha_sorter(self.filenames[filenames[0]]) == "keep_alpha":
            color_images = []
            alpha_images = []
            for filename in filenames:
                array = np.array(Image.open(self.filenames[filename]))
                color_images.append(Image.fromarray(np.squeeze(array[:, :, :-1])))
                alpha_images.append(Image.fromarray(array[:, :, -1]))
            color_image = hstack_images(*color_images)
            alpha_image = hstack_images(*alpha_images)
            return vstack_images(color_image, alpha_image)

        return hstack_images(
            *[Image.open(self.filenames[filename]) for filename in filenames]
        )
