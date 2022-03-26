#!/usr/bin/env python
#   pipescaler/core/cl/configurable_command_line_tool.py
#
#   Copyright (C) 2017-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""General-purpose configurable command-line tool base class"""
from abc import ABC
from argparse import ArgumentParser
from inspect import cleandoc
from logging import info
from os import environ
from os.path import expandvars, normpath
from typing import Any

from pipescaler.common import CommandLineTool
from pipescaler.core.file import read_yaml


class ConfigurableCommandLineTool(CommandLineTool, ABC):
    """General-purpose configurable command-line tool base class"""

    @classmethod
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """
        Construct argument parser

        Arguments:
            kwargs: Additional keyword arguments
        Returns:
            parser: Argument parser
        """
        description = kwargs.pop(
            "description", cleandoc(cls.__doc__) if cls.__doc__ is not None else ""
        )
        parser = super().construct_argparser(description=description, **kwargs)

        # Input
        parser.add_argument(
            "conf_file",
            type=cls.input_path_arg(),
            help="path to yaml file from which to read configuration",
        )

        return parser

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
