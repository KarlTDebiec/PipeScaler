#!python
#   lauseuisin/LauhSeuiSin.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
################################### MODULES ###################################
from __future__ import annotations

from argparse import ArgumentError, ArgumentParser, RawDescriptionHelpFormatter
from os import R_OK, access
from os.path import expandvars, isfile
from pathlib import Path

import yaml
from IPython import embed

from lauhseuisin.Pipeline import Pipeline


################################### CLASSES ###################################
class LauhSeuiSin:
    """
    TODO:
        - Support multiple LODs per image
        - Create symlink when creating LODs
        - Skip _0 files
        - Allow LODProcessor to also filter LOD files
        - Clean up LOD assignments for images with transparency
        - Clean up Water LODs
        - Errata
           - Smoke at Death Mountain crater
           - Phanton Ganon
           - Ghoma
        - Text
            - Title
                - tex1_256x32_9103FA5D9AB4FDFA_4
                - tex1_256x32_00498CD1C571BF89_4
            - THE END: tex1_128x32_3149F395AE28A5F7_5
        - Lighting & Shadows
            - Link's feet
            - Temple of time
            - Wallmaster
        - Maps
            - Some were erroneously compressed
            - Clean up using Nintendo 64 originals
        - Interface
            - STHeiti 80 point, STHeiti 56 point
        - Tiny eyes
            - tex1_16x16_DD8E1499FC36B179_13
            - tex1_32x32_14FB2897C9E5A3E4_2
            - tex1_32x32_3C53D10ED9BFAE42_2
            - tex1_32x32_7FB68131695743CC_2
        - Split Zelda files into separate repository
        - Move infile_argument to a module-level function
    """
    # region Class Variables

    package_root: str = str(Path(__file__).parent.absolute())

    # endregion

    # region Builtins

    def __init__(self, conf_file: str, verbosity: int = 1) -> None:
        """
        Initializes

        Args:
            conf_file (str): file from which to load configuration
        """
        # Read configuration file
        with open(conf_file, "r") as f:
            conf = yaml.load(f, Loader=yaml.SafeLoader)

        # Build pipeline
        self.pipeline = Pipeline(conf, verbosity=verbosity)

    def __call__(self):
        self.pipeline()

    # endregion

    # region Class Methods

    @classmethod
    def construct_argparser(cls) -> ArgumentParser:
        """
        Constructs argument parser

        Returns:
            parser (ArgumentParser): Argument parser
        """

        def infile_argument(value: str) -> str:
            if not isinstance(value, str):
                raise ArgumentError()

            value = expandvars(value)
            if not isfile(value):
                raise ArgumentError(f"infile '{value}' does not exist")
            elif not access(value, R_OK):
                raise ArgumentError(f"infile '{value}' cannot be read")

            return value

        parser = ArgumentParser(
            description=__doc__,
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
        parser.add_argument(
            "conf_file",
            type=infile_argument,
            help="configuration file")

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
    LauhSeuiSin.main()
