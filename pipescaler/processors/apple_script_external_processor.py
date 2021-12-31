#!/usr/bin/env python
#   pipescaler/processors/apple_script_external_processor.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Runs image through an AppleScript"""
from __future__ import annotations

from argparse import ArgumentParser
from inspect import cleandoc
from logging import debug, info
from os.path import join, split
from shutil import copyfile
from typing import Any

from pipescaler.common import (
    package_root,
    run_command,
    temporary_filename,
    validate_executable,
    validate_input_path,
)
from pipescaler.core import Processor


class AppleScriptExternalProcessor(Processor):
    """
    Runs image through an
    [AppleScript](https://developer.apple.com/library/archive/documentation/AppleScript/Conceptual/AppleScriptLangGuide/introduction/ASLR_intro.html);
    for example using
    [Pixelmator Pro](https://www.pixelmator.com/support/guide/pixelmator-pro/1270/).
    """

    def __init__(self, script: str, args: str = "", **kwargs: Any) -> None:
        """
        Validate and store static configuration

        Args:
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

    def __call__(self, infile: str, outfile: str) -> None:
        """
        Reads input image, processes it, and saves output image

        Arguments:
            infile: Input file path
            outfile: Output file path
        """
        command = validate_executable("osascript", {"Darwin"})

        with temporary_filename(".png") as tempfile:
            # Stage image
            copyfile(infile, tempfile)

            # Process image
            command += f' "{self.script}" "{tempfile}" {self.args}'
            debug(f"{self}: {command}")
            run_command(command)

            # Write image
            copyfile(tempfile, outfile)
            info(f"{self}: '{outfile}' saved")

    @classmethod
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """
        Construct argument parser

        Args:
            kwargs: Additional keyword arguments

        Returns:
            parser: Argument parser
        """
        description = kwargs.pop("description", cleandoc(cls.__doc__))
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
    AppleScriptExternalProcessor.main()
