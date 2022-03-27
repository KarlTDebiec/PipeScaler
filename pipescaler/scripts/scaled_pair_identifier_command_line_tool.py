#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
from __future__ import annotations

import itertools
from argparse import ArgumentParser
from inspect import cleandoc
from os.path import basename, splitext
from pprint import pprint
from shutil import move
from sys import exit
from typing import Any, Optional, Union

import numpy as np
import yaml
from IPython import embed
from PIL import Image
from skimage.metrics import structural_similarity as ssim

from pipescaler.common import (
    CommandLineTool,
    validate_float,
    validate_input_path,
    validate_output_path,
)
from pipescaler.core import get_files
from pipescaler.core.file import read_yaml


class ScaledPairIdentifierCommandLineTool(CommandLineTool):
    """"""

    exclusions = {".DS_Store", "desktop"}

    def __init__(
        self,
        input_directory: Union[str, list[str]],
        outfile: str,
        infile: str = None,
        output_directory: Optional[str] = None,
        threshold: float = 0.9,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

        # Input
        if infile is not None:
            self.scalesets = read_yaml(validate_input_path(infile))
            if self.scalesets is None:
                self.scalesets = {}
            pprint(self.scalesets)
        else:
            self.scalesets = {}

        if isinstance(input_directory, str):
            input_directory = [input_directory]
        input_directories = [
            validate_input_path(d, file_ok=False, directory_ok=True)
            for d in input_directory
        ]
        filenames = get_files(
            input_directories, style="absolute", exclusions=self.exclusions
        )
        self.filenames = {splitext(basename(f))[0]: f for f in filenames}

        # Operations
        self.threshold = validate_float(threshold, min_value=0, max_value=1)

        # Output
        self.outfile = validate_output_path(outfile)
        if output_directory is not None:
            self.output_directory = validate_output_path(
                output_directory, file_ok=False, directory_ok=True
            )
        else:
            self.output_directory = None

    def __call__(self, **kwargs: Any) -> None:

        self.load_data_and_thumbnails()

        try:
            # Loop over sizes from largest to smallest
            for size in list(reversed(sorted(self.data.keys()))):
                print(f"Reviewing {len(self.data[size])} images of {size}")

                # Loop over images at this size
                for name in self.data[size].keys():
                    print(f"Reviewing {name}")
                    self.review_image(name, size)

        except EOFError:
            self.quit()
        except KeyboardInterrupt:
            self.quit()

    @property
    def known_originals(self):
        return set(self.scalesets.keys())

    @property
    def known_scaled(self):
        return set(
            itertools.chain.from_iterable(
                [
                    [w for w in v.values() if not isinstance(w, list)]
                    for v in self.scalesets.values()
                ]
            )
        )

    def load_data_and_thumbnails(self):
        data = {}
        thumbnails = {}
        for filename in self.filenames.values():
            # Store full size data
            name = splitext(basename(filename))[0]
            image = Image.open(filename)
            size = image.size
            if size not in data:
                data[size] = {}
            data[size][name] = np.array(image)

            # Store thumbnail
            thumbnail_size = self.get_thumbnail_size(size)
            if thumbnail_size not in thumbnails:
                thumbnails[thumbnail_size] = {}
            thumbnails[thumbnail_size][name] = np.array(
                image.resize(thumbnail_size, resample=Image.LANCZOS)
            )

        self.data = data
        self.thumbnails = thumbnails

    def quit(self):
        # pprint(self.scalesets)
        with open(self.outfile, "w", encoding="utf-8") as outfile:
            yaml.dump(self.scalesets, outfile)
        print(f"Saved to {self.outfile}")
        exit()

    def review_image(self, original_name, original_size):
        if original_name in self.known_scaled:
            return

        original_datum = self.data[original_size][original_name]
        thumbnail_size = self.get_thumbnail_size(original_size)
        original_thumbnail = self.thumbnails[thumbnail_size][original_name]

        # Loop over scales from largest to smallest
        for scale in [0.5, 0.25, 0.125, 0.0625]:
            size = tuple(
                [
                    int(original_size[0] * scale),
                    int(original_size[1] * scale),
                ]
            )
            if size not in self.data:
                continue
            scaled = self.get_scaled(original_datum, size)

            # Loop over images of this size
            for small_name, small_datum in self.data[size].items():
                if original_name in self.scalesets:
                    if scale in self.scalesets[original_name]:
                        if self.scalesets[original_name][scale] == small_name:
                            move(self.filenames[small_name], self.output_directory)
                            print(
                                f"{self.filenames[small_name]} moved to "
                                f"{self.output_directory}"
                            )
                            continue
                    if "rejected" in self.scalesets[original_name]:
                        if small_name in self.scalesets[original_name]["rejected"]:
                            continue

                # Compare thumbnails, then full-sized images
                small_thumbnail = self.thumbnails[thumbnail_size][small_name]
                score = ssim(original_thumbnail, small_thumbnail, multichannel=True)
                if score < self.threshold / 2:
                    continue
                score = ssim(scaled, small_datum, multichannel=True)

                # Assess match
                if score > self.threshold:
                    print(f"{original_name}, {small_name}, {score}")
                    self.concatenate_images(original_datum, small_datum).show()
                    confirmation = input("Rescale pair? (y/n): ").lower()
                    if confirmation.startswith("y"):
                        if original_name not in self.scalesets:
                            self.scalesets[original_name] = {}
                        self.scalesets[original_name][scale] = small_name
                        pprint(self.scalesets[original_name])
                        with open(self.outfile, "w", encoding="utf-8") as outfile:
                            yaml.dump(self.scalesets, outfile)
                        print(f"Saved to {self.outfile}")
                        move(self.filenames[small_name], self.output_directory)
                        print(
                            f"{self.filenames[small_name]} moved to "
                            f"{self.output_directory}"
                        )
                    elif confirmation.startswith("n"):
                        if original_name not in self.scalesets:
                            self.scalesets[original_name] = {}
                        if "rejected" not in self.scalesets[original_name]:
                            self.scalesets[original_name]["rejected"] = []
                        self.scalesets[original_name]["rejected"].append(small_name)
                        pprint(self.scalesets[original_name])
                        with open(self.outfile, "w", encoding="utf-8") as outfile:
                            yaml.dump(self.scalesets, outfile)
                        print(f"Saved to {self.outfile}")
                    elif confirmation.startswith("e"):
                        embed()
                    elif confirmation.startswith("q"):
                        self.quit()

    @classmethod
    def concatenate_images(cls, *args):
        images = []
        size = None
        thumbnail_size = None
        for arg in args:
            if isinstance(arg, Image.Image):
                image = arg
            elif isinstance(arg, np.ndarray):
                image = Image.fromarray(arg)
            else:
                raise ValueError()

            if size is None:
                size = image.size
                thumbnail_size = cls.get_thumbnail_size(size)
            elif cls.get_thumbnail_size(image.size) != thumbnail_size:
                raise ValueError()

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

    @classmethod
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """
        Constructs argument parser.

        Arguments:
            kwargs (Any): Additional keyword arguments

        Returns:
            parser (ArgumentParser): Argument parser
        """
        description = kwargs.pop(
            "description", cleandoc(cls.__doc__) if cls.__doc__ is not None else ""
        )
        parser = super().construct_argparser(description=description, **kwargs)

        # Input
        parser_input = parser.add_argument_group("input arguments")
        parser_input.add_argument(
            "--infile",
            type=cls.input_path_arg(),
            help="input yaml file from which to read scaled file relationships",
        )
        parser_input.add_argument(
            "--input_directory",
            nargs="+",
            type=cls.input_path_arg(file_ok=True, directory_ok=True),
            help="input directories from which to read images",
        )

        # Operations
        parser_ops = parser.add_argument_group("operation arguments")
        parser_ops.add_argument(
            "--threshold",
            default=0.9,
            type=cls.float_arg(min_value=0, max_value=1),
            help="structural similarity index measure (SSIM) threshold "
            "(default: %(default)f)",
        )

        # Output
        parser_output = parser.add_argument_group("output arguments")
        parser_output.add_argument(
            "--outfile",
            required=True,
            type=cls.output_path_arg(),
            help="output yaml file to which to write scaled file relationships",
        )
        parser_output.add_argument(
            "--output_directory",
            required=False,
            type=cls.output_path_arg(file_ok=False, directory_ok=True),
            help="output directory to which to move scaled images",
        )

        return parser

    @staticmethod
    def get_scaled(datum, size):
        # noinspection PyTypeChecker
        return np.array(Image.fromarray(datum).resize(size, resample=Image.LANCZOS))

    @staticmethod
    def get_thumbnail_size(size):
        thumbnail_scale = max(8.0 / size[0], 8.0 / size[1])
        thumbnail_size = tuple(
            [int(size[0] * thumbnail_scale), int(size[1] * thumbnail_scale)]
        )

        return thumbnail_size


if __name__ == "__main__":
    ScaledPairIdentifierCommandLineTool.main()
