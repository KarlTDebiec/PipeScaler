#!/usr/bin/env python
#   pipescaler/scripts/pipe_runner.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from typing import Any

import yaml

from pipescaler.common import CLTool
from pipescaler.pipelines import Pipeline


####################################### CLASSES ########################################
class PipeScaler(CLTool):
    package_root: str = str(Path(__file__).parent.absolute())

    # region Builtins

    def __init__(self, conf_file: str, **kwargs) -> None:
        """
        Initializes

        Args:
            conf_file (str): file from which to load configuration
        """
        super().__init__(**kwargs)

        # Input
        with open(conf_file, "r") as f:
            conf = yaml.load(f, Loader=yaml.SafeLoader)
        self.pipeline = Pipeline(conf, verbosity=self.verbosity)

    def __call__(self) -> None:
        self.pipeline()

    # endregion

    # region Class Methods

    @classmethod
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """
        Constructs argument parser

        Returns:
            ArgumentParser: Argument parser
        """
        parser = super().construct_argparser(description=__doc__, **kwargs)

        # Input
        parser_input = parser.add_argument_group("input arguments")
        parser.add_argument(
            "conf_file", type=cls.input_path_argument(), help="configuration file"
        )

        return parser

    # endregion


######################################### MAIN #########################################
if __name__ == "__main__":
    PipeScaler.main()
