#!/usr/bin/env python
#   pydocstyle_reporter.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Prints pydocstyle results formatted for consumption by GitHub."""
from argparse import ArgumentParser
from inspect import cleandoc
from itertools import zip_longest
from os import environ, getenv
from os.path import normpath
from typing import Any

from pipescaler.common import CommandLineTool, run_command, validate_input_file


class PydocstyleReporter(CommandLineTool):
    """Prints pydocstyle results formatted for consumption by GitHub."""

    def __init__(
        self,
        pydocstyle_infile: str,
        modified_files_infile: str,
        **kwargs: Any,
    ):
        """Validate and store static configuration.

        Arguments:
            prospector_infile: Path to input prospector json output
            modified_files_infile: Path to input list of modified files
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        self.messages = []
        with open(validate_input_file(pydocstyle_infile)) as file:
            for line, issue in zip_longest(*[file] * 2):
                file, line = line.split()[0].split(":")
                code, message = issue.strip().split(": ")
                self.messages.append(
                    {"file": file, "line": line, "code": code, "message": message}
                )

        with open(validate_input_file(modified_files_infile)) as infile:
            self.modified_files = list(
                map(normpath, infile.read().strip("[]\n").split(","))
            )

    def __call__(self):
        """Perform operations."""
        self.report_summary()

        self.report_messages()

    def report_messages(self):
        info_messages = []
        warning_messages = []
        for pydocstyle_message in self.messages:
            filename = normpath(pydocstyle_message["file"])
            line = pydocstyle_message["line"]
            code = pydocstyle_message["code"]
            message = pydocstyle_message["message"]
            github_message = f"pydocstyle[{code}]: {message}"
            if filename in self.modified_files:
                warning_messages.append(
                    f"::warning file={filename},line={line}::{github_message}"
                )
            else:
                info_messages.append(
                    f"::info file={filename},line={line}::{github_message}"
                )
        for warning_message in warning_messages:
            print(warning_message)
        for info_message in info_messages:
            print(info_message)

    def report_summary(self):
        message_count = len(self.messages)
        github_message = f"pydocstyle reported {message_count} total messages"
        if message_count > 9:
            github_message += "; only the first 9 will appear as annotations"
        print(f"::warning::{github_message}")

    @classmethod
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """Construct argument parser.

        Arguments:
            **kwargs: Additional keyword arguments
        Returns:
            parser: Argument parser
        """
        description = kwargs.pop(
            "description", cleandoc(cls.__doc__) if cls.__doc__ is not None else ""
        )
        parser = super().construct_argparser(description=description, **kwargs)

        parser.add_argument(
            "pydocstyle_infile_infile",
            type=cls.input_path_arg(),
            help="Input pydocstyle output file",
        )

        parser.add_argument(
            "modified_files_infile",
            type=cls.input_path_arg(),
            help="Input list of added or modified files",
        )

        return parser


if __name__ == "__main__":
    PydocstyleReporter.main()
