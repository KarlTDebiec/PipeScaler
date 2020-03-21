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
        - Improve processing of very small images
        - Identify actors
        - Validate original LODs alongside scaled LODs
        - Split Zelda files into separate repository
        - Implement PeriodicProcessor
            - expand/contract flag to do/undo
            - cubic/radial flag
        - Water LODs:
            - tex1_64x64_C7BE133416AAC3CA_3.png
            - tex1_64x64_C8B91BCEB792B997_3.png
            - tex1_64x64_BD9806D0C00B08F7_12.png
            - tex1_64x64_BC039CA0695F021E_12.png
            - tex1_64x64_B18AB678D8BC5A9F_12.png
            - tex1_64x64_B24DE3E7113C3609_12.png
            - tex1_64x64_87040B6688EEF258_12.png
            - tex1_64x64_77377A9C56318449_12.png
            - tex1_64x64_6912F54E1173447A_12.png
            - tex1_64x64_636DAEEE24A17728_12.png
            - tex1_64x64_613F9A577B091D7E_12.png
            - tex1_64x64_503E3B07E0BC7DDA_12.png
            - tex1_64x64_76AF5635E42EBD9B_12.png
            - tex1_64x64_75DFB6378057B73A_12.png
            - tex1_64x64_66D51E8571B49E0F_12.png
            - tex1_64x64_59B09F068F3312B0_12.png
            - tex1_64x64_56DEA397DF612000_12.png
            - tex1_64x64_52AA260920F36315_12.png
            - tex1_64x64_030D5B706014F2EA_12.png
            - tex1_64x64_13E2EFE009408956_3.png
            - tex1_64x64_11BE0BD9FEAE32A8_12.png
            - tex1_64x64_8EB9669659A00DCD_12.png
            - tex1_64x64_8B6C90CCD54B2FF9_12.png
            - tex1_64x64_5FA6237A5B39DF51_12.png
            - tex1_64x64_5A6F17899691B74F_3.png
            - tex1_64x64_4BA1C6A8FA4BFED9_12.png
            - tex1_64x64_3C11751C3EDDAB35_12.png
            - tex1_64x64_2DB1C08C894FA060_12.png
            - tex1_64x64_2A8C4F28CA5A3FED_12.png
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
