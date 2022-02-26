#!/usr/bin/env python
#   pipescaler/processors/external/automator_processor.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Applies an Automator QuickAction to an image"""
from __future__ import annotations

from argparse import ArgumentParser
from inspect import cleandoc
from os.path import join, split
from typing import Any, Set

from pipescaler.common import package_root, validate_executable, validate_input_path
from pipescaler.core import ExternalProcessor


class AutomatorProcessor(ExternalProcessor):
    """
    Applies an
    [Automator QuickAction](https://support.apple.com/guide/automator/welcome/mac) to an
    image; for example using
    [Pixelmator Pro](https://www.pixelmator.com/support/guide/pixelmator-pro/1270/)
    """

    def __init__(self, workflow: str, **kwargs: Any) -> None:
        """
        Validate and store static configuration

        Arguments:
            workflow: Automator workflow to run
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Store configuration
        self.workflow = validate_input_path(
            workflow if workflow.endswith(".workflow") else f"{workflow}.workflow",
            file_ok=False,
            directory_ok=True,
            default_directory=join(*split(package_root), "data", "workflows"),
        )

    @property
    def command_template(self):
        """String template with which to generate command"""
        return (
            f"{validate_executable(self.executable, self.supported_platforms)}"
            " -i {infile}"
            f" {self.workflow}"
        )

    @property
    def executable(self) -> str:
        """Name of executable"""
        return "automator"

    @property
    def supported_platforms(self) -> Set[str]:
        """Platforms on which processor is supported"""
        return {"Darwin"}

    @classmethod
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """
        Construct argument parser

        Arguments:
            **kwargs: Additional keyword arguments

        Returns:
            parser: Argument parser
        """
        description = kwargs.pop(
            "description", cleandoc(cls.__doc__) if cls.__doc__ is not None else ""
        )
        parser = super().construct_argparser(description=description, **kwargs)

        # Operations
        parser.add_argument(
            "--workflow",
            type=cls.input_path_arg(
                file_ok=False,
                directory_ok=True,
                default_directory=join(*split(package_root), "data", "workflows"),
            ),
            help="path to workflow",
        )

        return parser


if __name__ == "__main__":
    AutomatorProcessor.main()
