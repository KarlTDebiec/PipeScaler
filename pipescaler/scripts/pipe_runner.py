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
from copy import deepcopy
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
        conf["stages"] = self.insert_subfiles(conf.get("stages", {}))

        # Parse blocks
        blocks = self.insert_subfiles(conf.pop("blocks", {}))
        blocks = self.insert_blocks(blocks, blocks)

        # Parse pipeline and pass on to Pipeline
        pipeline = conf.pop("pipeline")
        pipeline = self.insert_blocks(pipeline, blocks)
        conf["pipeline"] = pipeline

        self.pipeline = Pipeline(**conf)

    def __call__(self) -> None:
        self.pipeline()

    def insert_blocks(self, input, blocks):
        # TODO: Make this readable, most likely by creating output fresh
        if isinstance(input, dict):
            if len(input) == 1 and next(iter(input)) == "block":
                return deepcopy(blocks[input["block"]])
            else:
                for key in input:
                    input[key] = self.insert_blocks(input[key], blocks)
        elif isinstance(input, list):
            output = []
            for yat in input:
                new_stuff = self.insert_blocks(yat, blocks)
                if isinstance(new_stuff, list):
                    output.extend(new_stuff)
                else:
                    output.append(new_stuff)
            input = output
        return input

    def insert_subfiles(self, input):
        output = {}
        for key, value in input.items():
            if isinstance(value, str):
                with open(validate_input_path(value), "r") as f:
                    subfile = self.insert_subfiles(yaml.load(f, Loader=yaml.SafeLoader))
                    for sub_key, sub_value in subfile.items():
                        if sub_key not in output:
                            output[sub_key] = sub_value
                        else:
                            raise KeyError(f"'{sub_key}' specified multiple times")
            elif isinstance(value, dict) or isinstance(value, list):
                if key not in output:
                    output[key] = value
                else:
                    raise KeyError(f"'{key}' specified multiple times")
        return output

    @classmethod
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """
        Constructs argument parser.

        Returns:
            ArgumentParser: Argument parser
        """
        description = kwargs.pop("description", __doc__.strip())
        parser = super().construct_argparser(description=description, **kwargs)

        # Input
        parser.add_argument(
            "conf_file", type=cls.input_path_arg(), help="configuration file"
        )

        return parser


if __name__ == "__main__":
    PipeRunner.main()
