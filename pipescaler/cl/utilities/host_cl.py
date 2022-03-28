#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for Host."""
from __future__ import annotations

from argparse import ArgumentParser, _SubParsersAction
from logging import info
from os import environ
from os.path import expandvars, normpath
from typing import Type, Union

from pipescaler.core.cl import UtilityCommandLineTool
from pipescaler.core.file import read_yaml
from pipescaler.utilities import Host


class HostCL(UtilityCommandLineTool):
    """Command-line interface for Host."""

    @classmethod
    def add_arguments_to_argparser(
        cls,
        parser: Union[ArgumentParser, _SubParsersAction],
    ) -> None:
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: Nascent argument parser
        """
        required = cls.get_required_arguments_group(parser)
        required.add_argument(
            "conf_file",
            type=cls.input_path_arg(),
            help="path to yaml file from which to read configuration",
        )

    def __call__(self):
        """Perform operations."""
        raise NotImplementedError()

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

        utility = cls.utility(**{**kwargs, **conf})
        utility()

    @classmethod
    @property
    def utility(cls) -> Type:
        """Type of utility wrapped by command-line tool."""
        return Host


if __name__ == "__main__":
    HostCL.main()
