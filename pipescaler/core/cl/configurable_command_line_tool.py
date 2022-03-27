#!/usr/bin/env python
#   Copyright (C) 2017-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""General-purpose configurable command-line tool base class"""
from abc import ABC
from argparse import ArgumentParser, _SubParsersAction
from logging import info
from os import environ
from os.path import expandvars, normpath
from typing import Union

from pipescaler.common import CommandLineTool
from pipescaler.core.file import read_yaml


class ConfigurableCommandLineTool(CommandLineTool, ABC):
    """General-purpose configurable command-line tool base class"""

    @classmethod
    def add_arguments_to_argparser(
        cls,
        parser: Union[ArgumentParser, _SubParsersAction],
    ) -> None:
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: Nascent argument parser
        """
        parser.add_argument(
            "conf_file",
            type=cls.input_path_arg(),
            help="path to yaml file from which to read configuration",
        )

    @classmethod
    def main(cls) -> None:
        """Parse arguments, construct tool, and call tool"""
        parser = cls.construct_argparser()
        kwargs = vars(parser.parse_args())

        conf = read_yaml(kwargs.pop("conf_file"))

        # Set environment variables
        for key, value in conf.pop("environment", {}).items():
            value = normpath(expandvars(value))
            environ[key] = normpath(expandvars(value))
            info(f"Environment variable '{key}' set to '{value}'")

        tool = cls(**{**kwargs, **conf})
        tool()
