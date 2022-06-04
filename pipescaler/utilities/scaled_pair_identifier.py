#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Identifies pairs of images in which one is rescaled from another."""
import re
from logging import info
from os.path import isfile, join
from typing import Optional

import numpy as np
import pandas as pd
from imagehash import (
    average_hash,
    colorhash,
    dhash,
    hex_to_flathash,
    hex_to_hash,
    phash,
    whash,
)
from PIL import Image
from scipy.stats import zscore

from pipescaler.common import validate_output_directory, validate_output_file
from pipescaler.core import hstack_images, label_image, vstack_images
from pipescaler.pipe.sorters import AlphaSorter, GrayscaleSorter


class ScaledPairIdentifier:
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
        filenames: dict[str, str],
        pairs_file: str,
        hash_file: Optional[str] = None,
        image_directory: Optional[str] = None,
        interactive: bool = True,
    ):
        """Validate and store configuration.

        Arguments:
            filenames: Filenames to review; keys are base filenames and values are
              absolute paths
            pairs_file: CSV file to read/write scaled image pairs
            hash_file: CSV file to read/write cache of image hashes
            image_directory: Directory to which to write stacked scaled image sets
            interactive: Whether to prompt for interactive review
        """
        # Store input and output paths
        self.filenames = filenames
        """Image filenames; keys are base names and values are absolute paths"""
        self.pairs_file = validate_output_file(pairs_file)
        """CSV file from which to read/write scaled image pairs"""
        self.hash_file = None
        """CSV file from which to read/write image hash cache"""
        if hash_file is not None:
            self.hash_file = validate_output_file(hash_file)
        self.image_directory = None
        """Directory to which to write stacked scaled image sets"""
        if image_directory is not None:
            self.image_directory = validate_output_directory(
                image_directory, create_directory=True
            )

        # Prepare DatFrame of image hashes
        self.hashes = pd.DataFrame(
            {
                **{
                    "filename": pd.Series(dtype="str"),
                    "scale": pd.Series(dtype="float"),
                    "width": pd.Series(dtype="int"),
                    "height": pd.Series(dtype="int"),
                    "mode": pd.Series(dtype="str"),
                    "type": pd.Series(dtype="str"),
                },
                **{
                    f"{hash_type} hash": pd.Series(dtype="str")
                    for hash_type in self.hash_types.keys()
                },
            }
        )
        """Image hashes"""
        if self.hash_file is not None and isfile(self.hash_file):
            self.hashes = pd.read_csv(self.hash_file)
            info(f"Image hashes read from '{self.hash_file}'")

        # Prepare DataFrame of image pairs
        self.pairs = pd.DataFrame(
            {
                "filename": pd.Series(dtype="str"),
                "scale": pd.Series(dtype="float"),
                "scaled filename": pd.Series(dtype="str"),
            }
        )
        """Image pairs"""
        if isfile(self.pairs_file):
            self.pairs = pd.read_csv(self.pairs_file)
            info(f"Scaled image pairs read from '{self.pairs_file}'")

        self.interactive = interactive

        # Prepare image sorters for image analysis
        self.alpha_sorter = AlphaSorter()
        """Alpha sorter"""
        self.grayscale_sorter = GrayscaleSorter()
        """Grayscale sorter"""

        # Hash images
        self._calculate_all_hashes()

    @property
    def children(self) -> set[str]:
        """Child images."""
        return set(self.pairs["scaled filename"])

    @property
    def parents(self) -> set[str]:
        """Parent images."""
        return set(self.pairs["filename"])

    def _calculate_all_hashes(self):
        """Calculate all image hashes."""
        hashes_changed = False
        hashed_filenames = set(self.hashes["filename"])

        for filename in self.filenames:
            if filename not in hashed_filenames:
                self.hashes = self.hashes.append(self.calculate_hashes(filename))
                hashed_filenames.add(filename)
                hashes_changed = True

        if hashes_changed:
            self.hashes = self.hashes.reset_index(drop=True)
            if self.hash_file is not None:
                self.hashes.to_csv(self.hash_file, index=False)
                info(f"Image hashes saved to '{self.hash_file}'")

    def calculate_hamming_distance(
        self, parent_hash: pd.Series, child_hash: pd.Series, hash_type: str
    ) -> int:
        """Calculate hamming distance of hash_type between parent and child.

        Arguments:
            parent_hash: Parent hash
            child_hash: Child hash
            hash_type: Type of hash
        Returns:
            Hamming distance of *hash_type* between *parent* and *child*
        """
        if hash_type == "color":
            return hex_to_flathash(
                parent_hash[f"{hash_type} hash"], 14
            ) - hex_to_flathash(child_hash[f"{hash_type} hash"], 14)

        return hex_to_hash(parent_hash[f"{hash_type} hash"]) - hex_to_hash(
            child_hash[f"{hash_type} hash"]
        )

    def calculate_hashes(self, filename: str) -> pd.DataFrame:
        """Calculate hashes of filename, including original size and scaled versions.

        Arguments:
            filename: Basename of file
        Returns:
            Hashes of filename, including original size and scaled versions
        """
        absolute_filename = self.filenames[filename]
        image = Image.open(absolute_filename)
        size = image.size
        if self.grayscale_sorter(absolute_filename) == "keep_rgb":
            mode = "RGB"
        else:
            mode = "L"
        if self.alpha_sorter(absolute_filename) == "keep_alpha":
            mode += "A"
        filetype = filename.split("_")[-1]
        hashes = []
        for scale in np.array([1 / (2**x) for x in range(0, 7)]):
            width = round(size[0] * scale)
            height = round(size[1] * scale)
            if width < 8 or height < 8:
                break
            scaled_image = (
                image.resize((width, height), Image.LANCZOS) if scale != 1.0 else image
            )
            hashes.append(
                {
                    **{
                        "filename": filename,
                        "scale": scale,
                        "width": width,
                        "height": height,
                        "mode": mode,
                        "type": filetype,
                    },
                    **{
                        f"{hash_type} hash": str(hash_function(scaled_image))
                        for hash_type, hash_function in self.hash_types.items()
                    },
                }
            )

        return pd.DataFrame(hashes)

    def calculate_pair_score(
        self, parent_hash: pd.Series, child_hash: pd.Series
    ) -> pd.Series:
        """Calculate hamming sum between a potential parent_hash and child_hash.

        Arguments:
            parent_hash: Hash of potential parent
            child_hash: Hash of potential child
        Returns:
            Potential parent/child pair information and score
        """
        score = parent_hash.copy(deep=True)
        score["scaled filename"] = child_hash["filename"]

        for hash_type in self.hash_types:
            score[f"{hash_type} hamming"] = self.calculate_hamming_distance(
                score, child_hash, hash_type
            )
        score["hamming sum"] = score[
            [f"{hash_type} hamming" for hash_type in self.hash_types]
        ].sum()

        return score

    def get_hashes(self, filename: str, scale: float = 1.0) -> pd.Series:
        """Get hashes of filename at scale.

        Arguments:
            filename: Base filename whose hashes to get
            scale: Scale at which to get hashes
        Returns:
            Hashes of *filename* at *scale*
        """
        return self.hashes.loc[
            (self.hashes["filename"] == filename) & (self.hashes["scale"] == scale)
        ].iloc[0]

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
                # noinspection PyTypeChecker
                array = np.array(Image.open(self.filenames[filename]))
                color_images.append(Image.fromarray(np.squeeze(array[:, :, :-1])))
                alpha_images.append(Image.fromarray(array[:, :, -1]))
            color_image = hstack_images(*color_images)
            alpha_image = hstack_images(*alpha_images)
            return vstack_images(color_image, alpha_image)
        else:
            return hstack_images(
                *[Image.open(self.filenames[filename]) for filename in filenames]
            )

    def get_pair(self, child: str) -> pd.DataFrame:
        """Get pair of child.

        Arguments:
            child: Basename of child
        Returns:
            Pair of child
        """
        return self.pairs.loc[self.pairs["scaled filename"] == child]

    def get_pairs(self, parent: str) -> pd.DataFrame:
        """Get pairs of parent.

        Arguments:
            parent: Basename of parent
        Returns:
            Pairs of *parent*
        """
        return self.pairs.loc[self.pairs["filename"] == parent]

    def get_pair_scores(self, parent: str) -> Optional[pd.DataFrame]:
        """Get pair scores of parent.

        Arguments:
            parent: Base filename of parent whose pairs to get
        Returns:
            Pair scores of *parent*
        """
        parent_hash = self.get_hashes(parent)
        pairs = self.get_pairs(parent)
        if len(pairs) > 1:
            scores = []
            for _, pair in pairs.iterrows():
                child_hash = self.get_hashes(pair["scaled filename"])
                score = self.calculate_pair_score(parent_hash, child_hash)
                scores.append(score)
            scores = pd.DataFrame(scores)

            return scores

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

    def identify_pairs(self):
        """Identify pairs."""
        # Loop over potential parent images starting from the largest
        parent_hashes = self.hashes.loc[
            (self.hashes["scale"] == 1.0)
            & ~(self.hashes["filename"].isin(self.children))
        ].sort_values(["width", "height", "filename"], ascending=False)
        for _, parent_hash in parent_hashes.iterrows():
            # Known children may change as parents are reviewed
            if parent_hash["filename"] in self.children:
                continue

            info(f"Searching for child images of '{parent_hash['filename']}'")
            known_pairs = self.get_pairs(parent_hash["filename"])
            new_pairs = []
            new_pair_scores = []
            for scale in np.array([1 / (2**x) for x in range(1, 7)]):
                width = round(parent_hash["width"] * scale)
                height = round(parent_hash["height"] * scale)
                if width < 8 or height < 8:
                    break
                if scale not in known_pairs["scale"].values:
                    child_score = self.seek_best_child_score(parent_hash, scale)
                    if child_score is None:
                        break
                    new_pairs.append(
                        {
                            "filename": parent_hash["filename"],
                            "scale": scale,
                            "scaled filename": child_score["filename"],
                        }
                    )
                    new_pair_scores.append(child_score)

            # Update image sets
            if len(new_pairs) > 0:
                new_pairs = pd.DataFrame(new_pairs)
                new_pair_scores = pd.DataFrame(new_pair_scores)
                result = self.review_candidate_pairs(
                    known_pairs, new_pairs, new_pair_scores
                )
                if result == 0:
                    break
            pair_scores = self.get_pair_scores(parent_hash["filename"])
            if pair_scores is not None:
                print(pair_scores)
                image = self.get_pair_score_image(pair_scores)
                outfile = join(self.image_directory, f"{parent_hash['filename']}.png")
                image.save(outfile)
                info(f"Scaled image saved to '{outfile}'")

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
                    self.pairs = self.pairs.append(new_pairs.iloc[i])
                    scaled_pairs_modified = True
                    info(f"{new_pairs.iloc[i]} accepted")
            if scaled_pairs_modified:
                self.pairs = self.pairs.sort_values(
                    ["filename", "scale"], ascending=False
                )
                self.pairs.to_csv(self.pairs_file, index=False)
                info(f"Scaled pairs saved to '{self.pairs_file}'")
            return 1
        elif quit_re.match(response):
            return 0

    def seek_best_child_score(
        self, parent_hash: pd.Series, scale: float
    ) -> Optional[pd.Series]:
        """Get the best child of provided parent at scale.

        Arguments:
            parent_hash: Parent hash
            scale: Scale of child relative to parent
        Returns:
            Score of the best candidate child of *parent* at *scale*
        """
        # Find the best candidate child
        candidate_child_hashes = self.seek_candidate_child_scores(parent_hash, scale)
        if len(candidate_child_hashes) >= 2:
            best_idx = candidate_child_hashes["hamming sum z score"].idxmin()
            if np.isnan(best_idx):
                info(
                    f"Cannot distinguish best child candidate of "
                    f"'{parent_hash['filename']}' from candidates:\n"
                    f"{candidate_child_hashes}"
                )
                return
            candidate_child_hash = candidate_child_hashes.loc[best_idx]
        elif len(candidate_child_hashes) == 1:
            candidate_child_hash = candidate_child_hashes.iloc[0]
        else:
            return

        # Find best candidate parent of candidate child
        candidate_parent_hashes = self.seek_candidate_parent_scores(
            candidate_child_hash, scale
        )
        if len(candidate_parent_hashes) >= 2:
            best_idx = candidate_parent_hashes["hamming sum z score"].idxmin()
            if np.isnan(best_idx):
                info(
                    f"Cannot distinguish best parent candidate of "
                    f"'{candidate_child_hash}' from candidates:\n"
                    f"{candidate_parent_hashes}"
                )
                return
            candidate_parent_hash = candidate_parent_hashes.loc[best_idx]
        elif len(candidate_parent_hashes) == 1:
            candidate_parent_hash = candidate_parent_hashes.iloc[0]
        else:
            return

        # Review child
        if parent_hash["filename"] == candidate_parent_hash["filename"]:
            if candidate_child_hash["hamming sum"] <= 75:
                return candidate_child_hash
        return

    def seek_candidate_child_scores(
        self, parent_hash: pd.Series, scale: float
    ) -> pd.DataFrame:
        """Get scores of all candidate children of provided parent at scale.

        Arguments:
            parent_hash: Parent hash
            scale: Scale of child relative to parent
        Returns:
            Scores of candidate children of *parent* at *scale*
        """
        # Select potential child images
        candidates = self.hashes.loc[
            (self.hashes["scale"] == 1.0)
            & (self.hashes["width"] == round(parent_hash["width"] * scale))
            & (self.hashes["height"] == round(parent_hash["height"] * scale))
            & (self.hashes["mode"] == parent_hash["mode"])
            & (self.hashes["type"] == parent_hash["type"])
        ].copy(deep=True)
        if len(candidates) == 0:
            return candidates

        # Calculate hamming distances of candidates and sum thereof
        for hash_type in self.hash_types:
            candidates[f"{hash_type} hamming"] = candidates.apply(
                lambda child_hash: self.calculate_hamming_distance(
                    parent_hash, child_hash, hash_type
                ),
                axis=1,
            )
        candidates["hamming sum"] = candidates[
            [f"{hash_type} hamming" for hash_type in self.hash_types]
        ].sum(axis=1)

        # Calculate z scores of hamming sums of candidates
        candidates["hamming sum z score"] = zscore(candidates["hamming sum"])
        candidates = candidates.sort_values(["hamming sum z score"])
        candidates["hamming sum z score diff"] = list(
            np.diff(candidates["hamming sum z score"])
        ) + [np.nan]

        return candidates

    def seek_candidate_parent_scores(
        self, child_hash: pd.Series, scale: float
    ) -> pd.DataFrame:
        """Get scores of all candidate parents of provided child_hash at scale.

        Arguments:
            child_hash: Child hash
            scale: Scale of child relative to parent
        Returns:
            Scores of candidate parents of child at scale
        """
        # Select potential parent images
        candidates = self.hashes.loc[
            (self.hashes["scale"] == 1.0)
            & (self.hashes["width"] == round(child_hash["width"] / scale))
            & (self.hashes["height"] == round(child_hash["height"] / scale))
            & (self.hashes["mode"] == child_hash["mode"])
            & (self.hashes["type"] == child_hash["type"])
        ].copy(deep=True)
        if len(candidates) == 0:
            return candidates

        # Calculate hamming distances of candidates and sum thereof
        for hash_type in self.hash_types:
            candidates[f"{hash_type} hamming"] = candidates.apply(
                lambda parent_hash: self.calculate_hamming_distance(
                    parent_hash, child_hash, hash_type
                ),
                axis=1,
            )
        candidates["hamming sum"] = candidates[
            [f"{hash_type} hamming" for hash_type in self.hash_types]
        ].sum(axis=1)

        # Calculate z scores of hamming sums of candidates
        candidates["hamming sum z score"] = zscore(candidates["hamming sum"])
        candidates = candidates.sort_values(["hamming sum z score"])
        candidates["hamming sum z score diff"] = list(
            np.diff(candidates["hamming sum z score"])
        ) + [np.nan]

        return candidates
