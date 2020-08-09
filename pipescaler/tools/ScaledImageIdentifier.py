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
from typing import Dict, Set, Tuple

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
        conf = f"{getenv('HOME')}/OneDrive/code/Zelda3DHD/OOT"
        local = f"{getenv('HOME')}/Documents/OOT"

        with open(f"{conf}/interface.yaml", "r") as f:
            interface = yaml.load(f, Loader=yaml.SafeLoader)
        with open(f"{conf}/large_text.yaml", "r") as f:
            large_text = yaml.load(f, Loader=yaml.SafeLoader)
        with open(f"{conf}/maps.yaml", "r") as f:
            maps = yaml.load(f, Loader=yaml.SafeLoader)
        with open(f"{conf}/skip.yaml", "r") as f:
            skip = yaml.load(f, Loader=yaml.SafeLoader)

        # Construct dictionary of sizes to sets of images
        images: Dict[Tuple[int, int], Set[str]] = {}
        for infile in listdir(f"{local}/1x"):
            if infile == ".DS_Store":
                continue
            image = Image.open(f"{local}/1X/{infile}")
            size = image.size
            if size not in images:
                images[size] = set()
            images[size].add(infile)

        # Loop over sizes from largest to smallest
        for size in reversed(sorted(images.keys())):
            print(f"{size}: {len(images[size])}")

            # Loop over images at this size
            for large_infile in images[size]:
                large_image = Image.open(f"{local}/1X/{large_infile}")

                # Loop over scales from largest to smallest
                for scale in [0.5, 0.25, 0.125, 0.0625]:
                    scaled_size = tuple([int(size[0] * scale),
                                         int(size[1] * scale)])
                    if scaled_size not in images:
                        continue
                    print(f"    {scaled_size}: {len(images[scaled_size])}")
                    scaled_image = large_image.resize(scaled_size,
                                                      resample=Image.LANCZOS)
                    scaled_datum = np.array(scaled_image)

                    for small_infile in images[scaled_size]:
                        small_image = Image.open(f"{local}/1X/{small_infile}")
                        small_datum = np.array(small_image)
                        if scaled_datum.shape != small_datum.shape:
                            continue
                        score = ssim(scaled_datum, small_datum,
                                     multichannel=True)
                        if score > 0.9:
                            print(f"        {large_infile} {small_infile} "
                                  f"{score:4.2f}")

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
