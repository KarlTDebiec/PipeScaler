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
        - CLI for WaifuPixelmator2xTransparentProcessor
        - Identify actors
        - Validate original LODs alongside scaled LODs
        - Split Zelda files into separate repository
        - Implement PeriodicProcessor
            - expand/contract flag to do/undo
            - cubic/radial flag
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

    # region Public Class Methods

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
