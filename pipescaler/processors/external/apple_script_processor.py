#!/usr/bin/env python
#   pipescaler/processors/external/apple_script_processor.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Runs image through an AppleScript"""
from __future__ import annotations

from argparse import ArgumentParser
from inspect import cleandoc
from os.path import join, split
from typing import Any, Set

from pipescaler.common import package_root, validate_executable, validate_input_path
from pipescaler.core import ExternalProcessor


class AppleScriptProcessor(ExternalProcessor):
    """
    Runs image through an
    [AppleScript](https://developer.apple.com/library/archive/documentation/AppleScript/Conceptual/AppleScriptLangGuide/introduction/ASLR_intro.html);
    for example using
    [Pixelmator Pro](https://www.pixelmator.com/support/guide/pixelmator-pro/1270/)
    """

    def __init__(self, script: str, args: str = "", **kwargs: Any) -> None:
        """
        Validate and store static configuration

        Arguments:
            script: Path to AppleScript to run
            args: Arguments to pass to AppleScript
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Store configuration
        if not script.endswith(".scpt"):
            script = f"{script}.scpt"
        self.script = validate_input_path(
            script,
            default_directory=join(*split(package_root), "data", "scripts"),
        )
        self.args = args

    @property
    def command_template(self):
        """String template with which to generate command"""
        return (
            f"{validate_executable(self.executable, self.supported_platforms)}"
            f' "{self.script}"'
            ' "{infile}"'
            f" {self.args}"
        )

    @property
    def executable(self) -> str:
        """Name of executable"""
        return "osascript"

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
            "--script",
            type=cls.input_path_arg(
                default_directory=join(*split(package_root), "data", "scripts"),
            ),
            help="path to script",
        )
        parser.add_argument(
            "--args",
            type=str,
            help="arguments to pass to script",
        )

        return parser


if __name__ == "__main__":
    AppleScriptProcessor.main()
