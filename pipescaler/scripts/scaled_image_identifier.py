#!/usr/bin/env python
#   pipescaler/scripts/scaled_image_identifier.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
""""""
################################### MODULES ###################################
from __future__ import annotations

from argparse import ArgumentParser
from os import R_OK, W_OK, access, getcwd, listdir
from os.path import basename, dirname, exists, expandvars, isdir, isfile, join, \
    splitext
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import numpy as np
import yaml
from IPython import embed
from PIL import Image
from skimage.metrics import structural_similarity as ssim

from pipescaler.common import CLTool


################################### CLASSES ###################################
class ScaledImageIdentifier(CLTool):

    # region Builtins

    def __init__(self,
                 dump_directory: str,
                 skip: Optional[Union[List[str], str]] = None,
                 infile: Optional[str] = None,
                 threshold: float = 0.9,
                 outfile: Optional[str] = None,
                 concat_directory: Optional[str] = None,
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)

        # Input
        self.dump_directory = dump_directory
        if skip is not None:
            skip_files: Set[str] = set()
            for s in skip:
                if not exists(s):
                    raise ValueError()
                if isfile(s):
                    with open(s, "r") as f:
                        skip_files = skip_files.union(
                            set(yaml.load(f, Loader=yaml.SafeLoader)))
                elif isdir(s):
                    skip_files = skip_files.union(
                        set([splitext(f)[0] for f in listdir(s)]))
                else:
                    raise ValueError()
            self.skip_files = skip_files
        if infile is not None:
            with open(infile, "r") as f:
                self.known_scaled = yaml.load(f, Loader=yaml.SafeLoader)

        # Operations
        self.threshold = threshold

        # Output
        if outfile is not None:
            self.outfile = outfile
        self.concat_directory = concat_directory

    def __call__(self) -> None:

        # Load assigned images
        large_to_small = {}
        small_to_large = {}
        for large, scaled in self.known_scaled.items():
            large_to_small[large] = []
            for scale, smalls in scaled.items():
                if not isinstance(smalls, list):
                    smalls = [smalls]
                for small in smalls:
                    small_to_large[small] = (large, scale)
                    large_to_small[large].append((small, scale))
        self.skip_files = self.skip_files.union(small_to_large.keys())

        # Construct dictionary of sizes to dictionaries of images
        data: Dict[Tuple[int, int], Dict[str, np.ndarray]] = {}
        thumb_data: Dict[str, np.ndarray] = {}
        for infile in listdir(self.dump_directory):
            name, ext = splitext(infile)
            if infile == ".DS_Store" or name in self.skip_files:
                continue
            image = Image.open(f"{self.dump_directory}/{name}{ext}")
            size = image.size
            if size not in data:
                data[size] = {}
            data[size][name] = np.array(image)
            thumb_scale = max(8.0 / size[0], 8.0 / size[1])
            thumb_size = tuple(
                [int(size[0] * thumb_scale), int(size[1] * thumb_scale)])
            thumb_data[name] = np.array(
                image.resize(thumb_size, resample=Image.LANCZOS))

        # Loop over sizes from largest to smallest
        for size in list(reversed(sorted(data.keys()))):
            print(f"{size}: {len(data[size])}")
            for scale in [0.5, 0.25, 0.125, 0.0625]:
                scaled_size = tuple(
                    [int(size[0] * scale), int(size[1] * scale)])
                if scaled_size in data:
                    print(f"    {scaled_size}: {len(data[scaled_size])}")

            # Loop over images at this size
            i = 0
            for large_name, large_datum in data[size].items():
                print(large_name)
                large_thumb_datum = thumb_data[large_name]

                # Loop over scales from largest to smallest
                for scale in [0.5, 0.25, 0.125, 0.0625]:
                    scaled_size = tuple(
                        [int(size[0] * scale), int(size[1] * scale)])
                    if scaled_size not in data:
                        continue
                    scaled_datum = np.array(Image.fromarray(
                        large_datum).resize(scaled_size,
                                            resample=Image.LANCZOS))

                    # Loop over images of this size
                    for small_name, small_datum in data[scaled_size].items():
                        if scaled_datum.shape != small_datum.shape:
                            continue

                        # Check thumbnail
                        # embed()
                        small_thumb_datum = thumb_data[small_name]
                        score = ssim(large_thumb_datum, small_thumb_datum,
                                     multichannel=True)
                        if score < self.threshold / 2:
                            continue

                        # Check full size
                        score = ssim(scaled_datum, small_datum,
                                     multichannel=True)
                        if score > self.threshold:
                            print(f"        {i:4d} {large_name} "
                                  f"{small_name} {scale:6.4f} {score:4.2f}")
                            Image.fromarray(large_datum).show()
                            Image.fromarray(small_datum).show()
                i += 1

    # endregion

    # region Properties

    @property
    def concat_directory(self) -> Optional[str]:
        """str: Directory to which to write concatenated image files"""
        if not hasattr(self, "concat_directory"):
            self._concat_directory: Optional[str] = None
        return self._concat_directory

    @concat_directory.setter
    def concat_directory(self, value: Optional[str]) -> None:
        if value is not None:
            if not isinstance(value, str):
                raise ValueError(f"'{value}' is of type '{type(value)}', not "
                                 f"str")
            value = expandvars(value)
            if not exists(value):
                raise ValueError(f"'{value}' does not exist")
            if not isdir(value):
                raise ValueError(f"'{value}' exists but is not a directory")
            if not access(value, W_OK):
                raise ValueError(f"'{value}' exists but cannot be written")
        self._concat_directory = value

    @property
    def dump_directory(self) -> str:
        """str: Directory from which to load image files"""
        return self._dump_directory

    @dump_directory.setter
    def dump_directory(self, value: str) -> None:
        if not isinstance(value, str):
            raise ValueError(f"'{value}' is of type '{type(value)}', not str")
        value = expandvars(value)
        if not exists(value):
            raise ValueError(f"'{value}' does not exist")
        if not isdir(value):
            raise ValueError(f"'{value}' exists but is not a directory")
        if not access(value, R_OK):
            raise ValueError(f"'{value}' exists but cannot be read")
        self._dump_directory = value

    @property
    def known_scaled(self) -> Dict[str, Dict[float, Union[str, List[str]]]]:
        """Dict[float, Union[str, List[str]]]]: known scaled relationships"""
        if not hasattr(self, "_known_scaled"):
            self._known_scaled: Dict[
                str, Dict[float, Union[str, List[str]]]] = {}
        return self._known_scaled

    @known_scaled.setter
    def known_scaled(self, value: Dict[
        str, Dict[float, Union[str, List[str]]]]) -> None:
        self._known_scaled = value

    @property
    def outfile(self) -> Optional[str]:
        """Optional[str]: Directory from which to load image files"""
        if not hasattr(self, "outfile"):
            self._outfile: Optional[str] = None
        return self._outfile

    @outfile.setter
    def outfile(self, value: str) -> None:
        if value is not None:
            if not isinstance(value, str):
                raise ValueError(f"'{value}' is of type '{type(value)}', not "
                                 f"str")
            value = expandvars(value)
            directory = dirname(value)
            if directory == "":
                directory = getcwd()
            value = join(directory, basename(value))
            if exists(value):
                if not isfile(value):
                    raise ValueError(f"'{value}' exists but is not a file")
                if not access(value, W_OK):
                    raise ValueError(f"'{value}' exists but cannot be written")
            else:
                if not exists(directory):
                    raise ValueError(f"'{directory}' does not exist")
                if not isdir(directory):
                    raise ValueError(f"'{directory}' exists but is not a "
                                     f"directory")
                if not access(directory, W_OK):
                    raise ValueError(f"'{directory}' exists but cannot be "
                                     f"written")
        self._outfile = value

    @property
    def skip_files(self) -> Set[str]:
        """Set[str]: Files to skip if found in dump directory"""
        if not hasattr(self, "_skip_files"):
            self._skip_files: Set[str] = set()
        return self._skip_files

    @skip_files.setter
    def skip_files(self, value: Set[str]) -> None:
        self._skip_files = value

    @property
    def threshold(self) -> float:
        """
        float: Threshold structural similarity above which images are
        considered to match
        """
        return self._threshold

    @threshold.setter
    def threshold(self, value: float) -> None:
        try:
            value = float(value)
        except ValueError:
            raise ValueError(f"'{value}' is of type '{type(value)}', not "
                             f"float")
        if value < 0:
            raise ValueError(f"'{value}' is less than minimum value of 0.0")
        elif value > 1:
            raise ValueError(f"'{value}' is greater than maximum value of 1.0")
        self._threshold = value

    # endregion

    # region Class Methods

    @classmethod
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """
        Constructs argument parser

        Args:
            kwargs (Any): Additional keyword arguments

        Returns:
            ArgumentParser: Argument parser
        """
        parser = super().construct_argparser(description=__doc__, **kwargs)

        # Input
        parser_input = parser.add_argument_group("input arguments")
        parser_input.add_argument(
            "-d", "--dump",
            dest="dump_directory",
            metavar="DIR",
            required=True,
            type=cls.indir_argument(),
            help="input directory from which to read images")
        parser_input.add_argument(
            "-s", "--skip",
            metavar="FILE|DIR",
            nargs="+",
            type=cls.indir_or_infile_argument(),
            help="input file(s) from which to read lists of files to skip, or "
                 "input directories whose contained filenames should be "
                 "skipped")
        parser_input.add_argument(
            "-i", "--infile",
            metavar="FILE",
            type=cls.infile_argument(),
            help="input yaml file from which to read known scaled file "
                 "relationships")

        # Operations
        parser_ops = parser.add_argument_group("operation arguments")
        parser_ops.add_argument(
            "-t", "--threshold",
            default=0.9,
            type=cls.float_argument(0, 1),
            help="threshold")

        # Output
        parser_output = parser.add_argument_group("output arguments")
        parser_output.add_argument(
            "-o", "--outfile",
            metavar="FILE",
            type=cls.outfile_argument(),
            help="output yaml file to which to write scaled file "
                 "relationships")
        parser_output.add_argument(
            "-c", "--concat",
            metavar="FILE",
            type=cls.outdir_argument(),
            help="output directory to which to write concatenated images")

        return parser

    @classmethod
    def main(cls) -> None:
        """Parses and validates arguments, constructs and calls object"""
        parser = cls.construct_argparser()
        kwargs = vars(parser.parse_args())
        cls(**kwargs)()

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    ScaledImageIdentifier.main()
