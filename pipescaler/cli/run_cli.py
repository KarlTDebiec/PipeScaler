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
        """TODO: Refactor and remove requirement that this builtin be implemented."""
        return

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
    def insert_blocks(
        cls, input_section: Union[dict[str, Any], list[str]], blocks: dict[str, Any]
    ) -> Union[dict[str, Any], list[str]]:
        """Substitute blocks into a nascent configuration section.

        Arguments:
            input_section: Nascent configuration section
            blocks: Available blocks
        Returns:
            Configuration section with blocks inserted
        """
        if isinstance(input_section, dict):
            output_dict = {}
            if len(input_section) == 1 and next(iter(input_section)) == "block":
                return deepcopy(blocks[input_section["block"]])
            for key in input_section:
                output_dict[key] = cls.insert_blocks(input_section[key], blocks)
            return output_dict
        if isinstance(input_section, list):
            output_list = []
            for key in input_section:
                new_contents = cls.insert_blocks(key, blocks)
                if isinstance(new_contents, list):
                    output_list.extend(new_contents)
                else:
                    output_list.append(new_contents)
            return output_list
        return deepcopy(input_section)

    @classmethod
    def insert_subfiles(cls, input_section: dict[str, Any]) -> dict[str, Any]:
        """Insert contents of subfiles into a nascent section of a configuration.

        Arguments:
            input_section: Section into which subfile contents are to be inserted
        Returns:
            Updated section
        """
        output_section = {}
        for key, value in input_section.items():
            if isinstance(value, str):
                subfile = cls.insert_subfiles(read_yaml(validate_input_path(value)))
                for sub_key, sub_value in subfile.items():
                    if sub_key not in output_section:
                        output_section[sub_key] = sub_value
                    else:
                        raise KeyError(f"'{sub_key}' specified multiple times")
            elif isinstance(value, (dict, list)):
                if key not in output_section:
                    output_section[key] = value
                else:
                    raise KeyError(f"'{key}' specified multiple times")
        return output_section

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
