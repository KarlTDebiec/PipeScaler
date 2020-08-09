#!/usr/bin/env python
#   pipescaler/tools/ScaledImageIdentifier.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
################################### MODULES ###################################
from __future__ import annotations

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from os import getenv, listdir
from os.path import splitext
from typing import Dict, Tuple

import numpy as np
import yaml
from PIL import Image
from skimage.metrics import structural_similarity as ssim


################################### CLASSES ###################################
class ScaledImageIdentifier:

    # region Builtins

    def __init__(self, verbosity: int = 1) -> None:
        pass
        # Store input directory
        # Store list of files to ignore
        # Store dictionary of known scaled images
        # Store threshold
        # Store output directory for individual scaled images
        # Store output directory for concatenations

    def __call__(self):
        # conf = f"{getenv('HOME')}/OneDrive/code/Zelda3DHD/OOT"
        # local = f"{getenv('HOME')}/Documents/OOT"
        conf = f"{getenv('HOME')}/OneDrive/code/JSRHD/JSR"
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
        with open(f"{conf}/scaled.yaml", "r") as f:
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
        # for size in reversed(sorted(data.keys())):
        for size in [(256, 256)]:
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
    def construct_argparser(cls) -> ArgumentParser:
        """
        Constructs argument parser

        Returns:
            parser (ArgumentParser): Argument parser
        """
        parser = ArgumentParser(description=__doc__,
                                formatter_class=RawDescriptionHelpFormatter)
        verbosity = parser.add_mutually_exclusive_group()
        verbosity.add_argument(
            "-v", "--verbose",
            action="count",
            default=1,
            dest="verbosity",
            help="enable verbose output, may be specified more than once")
        verbosity.add_argument(
            "-q", "--quiet",
            action="store_const",
            const=0,
            dest="verbosity",
            help="disable verbose output")

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
