#!/usr/bin/env python
#   pipescaler/processors/automator_external_processor.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Applies an Automator QuickAction to an image"""
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


class AutomatorExternalProcessor(Processor):
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

    def __call__(self, infile: str, outfile: str) -> None:
        """
        Read image from infile, process it, and save to outfile

        Arguments:
            infile: Input file path
            outfile: Output file path
        """
        command = validate_executable("automator", {"Darwin"})

        with temporary_filename(".png") as tempfile:
            # Stage image
            copyfile(infile, tempfile)

            # Process image
            command += f" -i {tempfile} {self.workflow}"
            debug(f"{self}: {command}")
            run_command(command)

            # Write image
            copyfile(tempfile, outfile)
            info(f"{self}: '{outfile}' saved")

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
    AutomatorExternalProcessor.main()
