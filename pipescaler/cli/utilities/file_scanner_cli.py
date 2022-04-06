#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Command line interface for FileScanner."""
from __future__ import annotations

from argparse import ArgumentParser, _SubParsersAction
from logging import info
from os import environ
from os.path import expandvars, normpath
from typing import Any, Type, Union

from pipescaler.common import set_logging_verbosity, validate_int
from pipescaler.core.cli import UtilityCli
from pipescaler.core.file import read_yaml
from pipescaler.utilities import FileScanner


class FileScannerCli(UtilityCli):
    """Command line interface for FileScanner."""

    def __call__(self):
        """Perform operations."""
        raise NotImplementedError()

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

        # noinspection PyCallingNonCallable
        utility = cls.utility(**{**kwargs, **conf})
        utility()

    @classmethod
    @property
    def utility(cls) -> Type:
        """Type of utility wrapped by command line interface."""
        return FileScanner


if __name__ == "__main__":
    FileScannerCli.main()
