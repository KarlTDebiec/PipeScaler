#!/usr/bin/env python
#   pipescaler/scripts/pipe_runner.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
""""""
from __future__ import annotations

from argparse import ArgumentParser
from os import environ
from os.path import expandvars, normpath
from typing import Any

import yaml

from pipescaler.common import CLTool, validate_input_path
from pipescaler.core.pipeline import Pipeline


class PipeRunner(CLTool):
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

        # Set environment variables
        for key, value in conf.pop("environment", {}).items():
            environ[key] = normpath(expandvars(value))

        # Parse stages from external file
        conf["stages"] = self.parse_stages(conf.get("stages", {}))

        # Pass on fully-parsed conf to Pipeline to initialize
        self.pipeline = Pipeline(**conf)

    def __call__(self) -> None:
        self.pipeline()

    def parse_stages(self, input_stages):
        output_stages = {}
        for stage_name, stage_conf in input_stages.items():
            if isinstance(stage_conf, str):
                with open(validate_input_path(stage_conf), "r") as f:
                    stage_conf = yaml.load(f, Loader=yaml.SafeLoader)
                sub_stages = self.parse_stages(stage_conf)
                for sub_stage_name, sub_stage_conf in sub_stages.items():
                    if sub_stage_name not in output_stages:
                        output_stages[sub_stage_name] = sub_stage_conf
                    else:
                        raise KeyError(
                            f"Stage name '{stage_name}' specified multiple times"
                        )
            elif isinstance(stage_conf, dict):
                if stage_name not in output_stages:
                    output_stages[stage_name] = stage_conf
                else:
                    raise KeyError(
                        f"Stage name '{stage_name}' specified multiple times"
                    )
        return output_stages

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


if __name__ == "__main__":
    PipeRunner.main()
