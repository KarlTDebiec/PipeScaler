#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Command line interface for PipelineRunner."""
from __future__ import annotations

from argparse import ArgumentParser, _SubParsersAction
from copy import deepcopy
from logging import info
from os import environ
from os.path import expandvars, normpath
from typing import Any, Type, Union

from pipescaler.common import (
    CommandLineInterface,
    set_logging_verbosity,
    validate_input_path,
    validate_int,
)
from pipescaler.core.file import read_yaml
from pipescaler.core.pipeline import Pipeline


class RunCli(CommandLineInterface):
    """Command line interface for PipelineRunner."""

    def __init__(self, **kwargs: Any) -> None:
        """Initializes."""
        super().__init__(**kwargs)

    def __call__(self) -> None:
        pass

    @classmethod
    def add_arguments_to_argparser(
        cls,
        parser: Union[ArgumentParser, _SubParsersAction],
    ) -> None:
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: Nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        required = cls.get_required_arguments_group(parser)
        required.add_argument(
            "conf_file",
            type=cls.input_path_arg(),
            help="yaml file from which to read configuration",
        )

    @classmethod
    def insert_blocks(cls, input, blocks):
        # TODO: Make this readable, most likely by creating output fresh
        if isinstance(input, dict):
            if len(input) == 1 and next(iter(input)) == "block":
                return deepcopy(blocks[input["block"]])
            else:
                for key in input:
                    input[key] = cls.insert_blocks(input[key], blocks)
        elif isinstance(input, list):
            output = []
            for yat in input:
                new_stuff = cls.insert_blocks(yat, blocks)
                if isinstance(new_stuff, list):
                    output.extend(new_stuff)
                else:
                    output.append(new_stuff)
            input = output
        return input

    @classmethod
    def insert_subfiles(cls, input):
        output = {}
        for key, value in input.items():
            if isinstance(value, str):
                subfile = cls.insert_subfiles(read_yaml(validate_input_path(value)))
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
    def main(cls) -> None:
        """Parse arguments."""
        parser = cls.construct_argparser()
        kwargs = vars(parser.parse_args())
        cls.main2(**kwargs)

    @classmethod
    def main2(cls, **kwargs: Any) -> None:
        """Read configuration, configure environment, and build and call utility."""
        conf = read_yaml(kwargs.pop("conf_file"))

        # Set environment variables
        for key, value in conf.pop("environment", {}).items():
            value = normpath(expandvars(value))
            environ[key] = value
            info(f"Environment variable '{key}' set to '{value}'")

        verbosity = validate_int(kwargs.pop("verbosity", 0), min_value=0)
        set_logging_verbosity(verbosity)

        # Parse stages from external file
        conf["stages"] = cls.insert_subfiles(conf.get("stages", {}))

        # Parse blocks
        blocks = cls.insert_subfiles(conf.pop("blocks", {}))
        blocks = cls.insert_blocks(blocks, blocks)

        # Parse pipeline
        pipeline = conf.pop("pipeline")
        pipeline = cls.insert_blocks(pipeline, blocks)
        conf["pipeline"] = pipeline

        # Run pipeline
        utility = cls.utility(**{**kwargs, **conf})
        utility()

    @classmethod
    @property
    def description(cls) -> str:
        """Long description of this tool displayed below usage."""
        return "Runs a pipeline"

    @classmethod
    @property
    def help(cls) -> str:
        """Short description of this tool used when it is a subparser."""
        return "run a pipeline"

    @classmethod
    @property
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser."""
        return cls.__name__.removesuffix("Cli").lower()

    @classmethod
    @property
    def utility(cls) -> Type:
        """Type of utility wrapped by command line interface."""
        return Pipeline


if __name__ == "__main__":
    RunCli.main()
