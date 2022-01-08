#!/usr/bin/env python
#   common/configurable_command_line_tool.py
#
#   Copyright (C) 2017-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""General-purpose configurable command-line tool base class"""
from argparse import ArgumentParser
from inspect import cleandoc
from logging import info
from os import environ
from os.path import expandvars, normpath
from pprint import pprint
from typing import Any

from pipescaler.common import CommandLineTool
from pipescaler.core.file import read_yaml


class ConfigurableCommandLineTool(CommandLineTool):
    """General-purpose configurable command-line tool base class"""

    @classmethod
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """
        Construct argument parser

        Arguments:
            **kwargs: Additional keyword arguments

        Returns:
            Argument parser
        """
        description = kwargs.pop(
            "description", cleandoc(cls.__doc__) if cls.__doc__ is not None else ""
        )
        parser = super().construct_argparser(description=description, **kwargs)

        configuration = parser.add_argument_group("configuration")
        configuration.add_argument("--yat", help="yat")
        configuration.add_argument("--eee", help="eee")
        configuration.add_argument("--sam", help="sam")

        # Yaml subparser
        subparsers = parser.add_subparsers(title="sub-commands")
        yaml_subparser = subparsers.add_parser(
            "yaml",
            description="This is the yaml subparser description",
            help="read arguments from yaml file",
        )
        verbosity = yaml_subparser.add_mutually_exclusive_group()
        verbosity.add_argument(
            "-v",
            "--verbose",
            action="count",
            default=1,
            dest="verbosity",
            help="enable verbose output, may be specified more than once",
        )
        verbosity.add_argument(
            "-q",
            "--quiet",
            action="store_const",
            const=0,
            dest="verbosity",
            help="disable verbose output",
        )
        yaml_subparser.add_argument(
            "yaml_file",
            type=cls.input_path_arg(),
            help="path to yaml file from which to read arguments",
        )

        return parser

    @classmethod
    def main(cls) -> None:
        """Parse arguments, construct tool, and call tool"""
        parser = cls.construct_argparser()
        kwargs = vars(parser.parse_args())
        yaml_kwargs = {}

        if "yaml_file" in kwargs:
            yaml_kwargs = read_yaml(kwargs.pop("yaml_file"))
            for key, value in yaml_kwargs.pop("environment", {}).items():
                value = normpath(expandvars(value))
                environ[key] = value
                info(f"Set environment variable '{key}' to '{value}'")

        pprint(kwargs)
        pprint(yaml_kwargs)

        # tool = cls(**{**kwargs, **yaml_kwargs})
        # tool()
