#!/usr/bin/env python
#  Copyright (C) 2020-2022. Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Identifies pairs of images in which one is rescaled from another."""
import re
from itertools import chain
from logging import info
from pathlib import Path
from shutil import move
from typing import Iterable, Union

import numpy as np
import pandas as pd
from imagehash import average_hash, colorhash, dhash, phash, whash
from PIL import Image

from pipescaler.common import validate_input_directories, validate_input_directory
from pipescaler.core import Utility
from pipescaler.core.image import hstack_images, vstack_images
from pipescaler.core.image_hash_collection import ImageHashCollection
from pipescaler.core.image_pair_collection import ImagePairCollection
from pipescaler.core.image_pair_scorer import ImagePairScorer, ScoreDataFrame
from pipescaler.core.pipelines import PipeImage
from pipescaler.core.sorting import citra_sort
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
    ):
        """Validate configuration and initialize.

        Arguments:
            input_directories: Directory or directories from which to read input files
            project_root: Root directory of project
            pairs_file: CSV file to read/write scaled image pairs
            hash_file: CSV file to read/write cache of image hashes
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
        self.file_paths = {
            f.stem: f
            for f in chain.from_iterable(
                d.iterdir() for d in self.input_directories + [self.scaled_directory]
            )
        }
        self.hash_collection = ImageHashCollection(self.file_paths.values(), hash_file)
        """Image hashes."""
        self.pair_collection = ImagePairCollection(pairs_file)
        """Image pairs."""
        self.pair_scorer = ImagePairScorer(self.hash_collection)
        """Image pair scorer."""

        for name, file_path in self.file_paths.items():
            if name in self.pair_collection.children:
                if not file_path.is_relative_to(self.scaled_directory):
                    new_path = self.scaled_directory.joinpath(file_path.name)
                    move(file_path, new_path)
                    self.file_paths[name] = new_path
                    info(f"Moved {file_path} to {new_path}")
        for file_path in self.scaled_directory.iterdir():
            if file_path.stem not in self.pair_collection.children:
                new_path = self.input_directories[0].joinpath(file_path.name)
                move(file_path, new_path)
                self.file_paths[file_path.stem] = new_path
                info(f"Moved {file_path} to {new_path}")

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

    def identify_pairs(self) -> None:
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
            if len(new_scores) > 0:
                new_scores = pd.DataFrame(new_scores)
                result = self.review_candidate_pairs(known_scores, new_scores)
                if result == 0:
                    break
            else:
                if len(known_scores) > 0:
                    print("Known scores:")
                    print(known_scores)

    def known_scores(self, parent: str) -> ScoreDataFrame:
        return self.pair_scorer.get_pair_scores(
            self.pair_collection[parent]
        ).sort_values("scale", ascending=False)

    def save_images(self) -> None:
        for parent in sorted(
            self.pair_collection.parents, key=citra_sort, reverse=True
        ):
            known_scores = self.known_scores(parent)
            if len(known_scores) > 0:
                to_save = self.get_stacked_image(
                    [parent, *list(known_scores["scaled name"])]
                )
                outfile = self.comparison_directory.joinpath(f"{parent}.png")
                to_save.save(outfile)
                info(f"Saved {outfile}")

    def review_candidate_pairs(
        self, known_scores: ScoreDataFrame, new_scores: ScoreDataFrame
    ) -> int:
        """Review candidate pairs of parent image.

        Arguments:
            known_scores: Scores of known pairs
            new_scores: Scores of new pairs
        """
        print(
            f"To known pairs:\n"
            f"{known_scores}\n"
            f"may be added new pairs:\n"
            f"{new_scores}"
        )
        all_pairs = pd.concat((known_scores, new_scores)).sort_values(
            "scale", ascending=False
        )
        parent = all_pairs.iloc[0]["name"]
        children = list(all_pairs["scaled name"])

        if self.interactive:
            self.get_stacked_image([parent, *list(all_pairs["scaled name"])]).show()
        prompt = f"Confirm ({'y' * len(new_scores)}/{'n' * len(new_scores)})?: "
        accept_re = re.compile(f"^[yn]{{{len(new_scores)}}}$", re.IGNORECASE)
        quit_re = re.compile("quit", re.IGNORECASE)
        if self.interactive:
            response = input(prompt).lower()
        else:
            response = "y" * len(new_scores)
        if accept_re.match(response):
            new_pair = None
            for i in range(len(new_scores)):
                if response[i] == "y":
                    new_pair = pd.DataFrame(
                        [
                            {
                                "name": parent,
                                "scale": new_scores.iloc[i]["scale"],
                                "scaled name": new_scores.iloc[i]["scaled name"],
                            }
                        ]
                    )
                    self.pair_collection.add(new_pair)
                    info(f"{new_pair} accepted")
                if new_pair is not None:
                    self.pair_collection.save_cache()
            return 1
        elif quit_re.match(response):
            return 0

    def get_stacked_image(self, names: list[str]) -> Image.Image:
        """Get stacked images, rescaled to match first image, if necessary.

        Arguments:
            names: Names of files to stack
        Returns:
            Stacked images, rescaled to match first image, if necessary
        """
        if self.alpha_sorter(PipeImage(path=self.file_paths[names[0]])) == "keep_alpha":
            color_images = []
            alpha_images = []
            for name in names:
                array = np.array(Image.open(self.file_paths[name]))
                color_images.append(Image.fromarray(np.squeeze(array[:, :, :-1])))
                alpha_images.append(Image.fromarray(array[:, :, -1]))
            return vstack_images(
                hstack_images(*color_images), hstack_images(*alpha_images)
            )

        return hstack_images(
            *[Image.open(self.file_paths[filename]) for filename in names]
        )
