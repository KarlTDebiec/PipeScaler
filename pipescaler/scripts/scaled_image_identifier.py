#!/usr/bin/env python
#   pipescaler/tools/scaled_image_identifier.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
################################### MODULES ###################################
from __future__ import annotations

from argparse import ArgumentParser
from os import getenv, listdir
from os.path import splitext
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import yaml
from PIL import Image
from skimage.metrics import structural_similarity as ssim

from pipescaler.core import CLTool


################################### CLASSES ###################################
class ScaledImageIdentifier(CLTool):

    # region Builtins

    def __init__(self,
                 indir: str,
                 skip: Optional[Union[List[str], str]] = None,
                 scaled: Optional[str] = None,
                 threshold: float = 0.9,
                 concat_outdir: Optional[str] = None,
                 verbosity: int = 1,
                 **kwargs: Any) -> None:
        pass
        # Store output directory for individual scaled images
        # Store output directory for concatenations

    def __call__(self):
        print("called")
        return
        # conf = f"{getenv('HOME')}/OneDrive/code/PipeScalerProjects/ZeldaOOT3D"
        # local = f"{getenv('HOME')}/Documents/OOT"
        conf = f"{getenv('HOME')}/OneDrive/code/PipeScalerProjects/JetSetRadio"
        local = f"{getenv('HOME')}/Documents/JSR"

        skip = set(
            [splitext(f)[0] for f in listdir(f"{local}/1x_skip")])
        skip = skip.union(
            [splitext(f)[0] for f in listdir(f"{local}/1x_interface")])
        # skip = skip.union(
        #     [splitext(f)[0] for f in listdir(f"{local}/1x_large_text")])
        # skip = skip.union(
        #     [splitext(f)[0] for f in listdir(f"{local}/1x_maps")])
        # skip = skip.union(
        #     [splitext(f)[0] for f in listdir(f"{local}/1x_normal")])

        # Load assigned images
        with open(f"{conf}/classes/scaled.yaml", "r") as f:
            assignments = yaml.load(f, Loader=yaml.SafeLoader)
        large_to_small = {}
        small_to_large = {}
        for large, scaled in assignments.items():
            large_to_small[large] = []
            for scale, smalls in scaled.items():
                if not isinstance(smalls, list):
                    smalls = [smalls]
                for small in smalls:
                    small_to_large[small] = (large, scale)
                    large_to_small[large].append((small, scale))
        skip = skip.union(small_to_large.keys())

        # Construct dictionary of sizes to dictionaries of images
        data: Dict[Tuple[int, int], Dict[str, np.ndarray]] = {}
        for infile in listdir(f"{local}/1x"):
            if infile == ".DS_Store" or splitext(infile)[0] in skip:
                continue
            image = Image.open(f"{local}/1X/{infile}")
            size = image.size
            if size not in data:
                data[size] = {}
            data[size][splitext(infile)[0]] = np.array(image)

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
            for large_infile, large_datum in data[size].items():
                # print(large_infile)

                # Loop over scales from largest to smallest
                for scale in [0.5, 0.25, 0.125, 0.0625]:
                    scaled_size = tuple(
                        [int(size[0] * scale), int(size[1] * scale)])
                    if scaled_size not in data:
                        continue
                    # print(f"    {scaled_size}: {len(data[scaled_size])}")
                    scaled_datum = np.array(
                        Image.fromarray(large_datum).resize(
                            scaled_size, resample=Image.LANCZOS))

                    for small_infile, small_datum in data[scaled_size].items():
                        if small_infile == large_infile:
                            continue
                        if scaled_datum.shape != small_datum.shape:
                            continue
                        score = ssim(scaled_datum, small_datum,
                                     multichannel=True)

                        if score > 0.9:
                            print(f"        {i:4d} {large_infile} "
                                  f"{small_infile} {scale:6.4f} {score:4.2f}")
                            Image.fromarray(large_datum).show()
                            Image.fromarray(small_datum).show()
                i += 1

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
            "-i", "--indir",
            metavar="DIR",
            type=cls.indir_argument(),
            help="input directory from which to read files")
        parser_input.add_argument(
            "-s", "--skip",
            metavar="FILE|DIR",
            nargs="+",
            required=False,
            type=cls.indir_or_infile_argument(),
            help="input file(s) from which to read lists of files to skip, or "
                 "input directories whose contained filenames should be "
                 "skipped")
        parser_input.add_argument(
            "-a", "--asd",
            metavar="FILE",
            type=cls.infile_argument(),
            help="input yaml file from which to read scaled file "
                 "relationships")

        # Operations
        parser_ops = parser.add_argument_group("operation arguments")
        parser_ops.add_argument(
            "-t", "--threshold",
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
            "-c", "--concat_outdir",
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
