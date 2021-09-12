#!/usr/bin/env python
#   pipescaler/processors/apple_script_processor.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
""""""
from __future__ import annotations

from argparse import ArgumentParser
from logging import debug, info
from os.path import join, split
from shutil import copyfile
from subprocess import Popen
from sys import platform
from typing import Any

from pipescaler.common import (
    package_root,
    temporary_filename,
    validate_input_path,
)
from pipescaler.core import Processor, UnsupportedPlatformError


class AppleScriptProcessor(Processor):
    def __init__(self, script: str, args: str = "", **kwargs: Any) -> None:
        super().__init__(**kwargs)

        # Store configuration
        self.script = validate_input_path(
            script if script.endswith(".scpt") else f"{script}.scpt",
            default_directory=join(*split(package_root), "data", "scripts"),
        )
        self.args = args

    def __call__(self, infile: str, outfile: str) -> None:
        if platform != "darwin":
            raise UnsupportedPlatformError(
                "AppleScriptProcessor is only supported on macOS"
            )
        self.process_file(infile, outfile, script=self.script, args=self.args)

    @classmethod
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """
        Constructs argument parser.

        Args:
            kwargs (Any): Additional keyword arguments

        Returns:
            parser (ArgumentParser): Argument parser
        """
        description = kwargs.get("description", __doc__.strip())
        parser = super().construct_argparser(description=description, **kwargs)

        # Operations
        parser.add_argument(
            "--script",
            type=cls.input_path_arg(
                file_ok=False,
                directory_ok=True,
                default_directory=join(*split(package_root), "data", "scripts"),
            ),
            help="path to script",
        )

        return parser

    @classmethod
    def process_file(cls, infile: str, outfile: str, **kwargs: Any) -> None:
        script = kwargs.pop("script")
        args = kwargs.get("args", "")

        with temporary_filename(".png") as tempfile:
            # Stage image
            copyfile(infile, tempfile)

            # Run automator script
            command = f'osascript "{script}" "{tempfile}" {args}'
            debug(f"{cls}: {command}")
            Popen(command, shell=True, close_fds=True).wait()

            # Write image
            copyfile(tempfile, outfile)
            info(f"{cls}: '{outfile}' saved")


if __name__ == "__main__":
    AppleScriptProcessor.main()
