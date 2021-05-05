#!/usr/bin/env python
#   pipescaler/scripts/pipe_runner.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
""""""
####################################### MODULES ########################################
from __future__ import annotations

from argparse import ArgumentParser
from typing import Any

import yaml

from pipescaler.common import CLTool, validate_input_path
from pipescaler.core.pipeline import Pipeline


####################################### CLASSES ########################################
class PipeRunner(CLTool):

    # region Builtins

    def __init__(self, conf_file: str, **kwargs: Any) -> None:
        """
        Initializes.

        Args:
            conf_file (str): file from which to load configuration
        """
        super().__init__(**kwargs)

        # Input
        with open(validate_input_path(conf_file), "r") as f:
            conf = yaml.load(f, Loader=yaml.SafeLoader)
        self.pipeline = Pipeline(verbosity=self.verbosity, **conf)

    def __call__(self) -> None:
        self.pipeline()

    # endregion

    # region Class Methods

    @classmethod
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """
        Constructs argument parser.

        Returns:
            ArgumentParser: Argument parser
        """
        description = kwargs.get("description", __doc__.strip())
        parser = super().construct_argparser(description=description, **kwargs)

        # Input
        parser.add_argument(
            "conf_file", type=cls.input_path_arg(), help="configuration file"
        )

        return parser

    # endregion


######################################### MAIN #########################################
if __name__ == "__main__":
    PipeRunner.main()
