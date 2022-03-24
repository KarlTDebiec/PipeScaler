#!/usr/bin/env python
#   prospector_reporter.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Prints prospector results formatted for consumption by GitHub."""
import json
from argparse import ArgumentParser
from inspect import cleandoc
from os import environ, getenv
from os.path import normpath
from typing import Any

from pipescaler.common import CommandLineTool, run_command, validate_input_file


class ProspectorReporter(CommandLineTool):
    """Prints prospector results formatted for consumption by GitHub."""

    def __init__(self, infile, **kwargs):
        """Validate and store static configuration.

        Arguments:
            infile: Path to input prospector json output
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        with open(validate_input_file(infile)) as file:
            self.report = json.load(file)

        self.modified_files = None
        if "GITHUB_BASE_REF" in environ:
            command = f"git diff --name-status {getenv('GITHUB_BASE_REF')}"
            (exitcode, stdout, stderr) = run_command(command)
            self.modified_files = [
                normpath(line[1:].strip()) for line in stdout.strip().split("\n")
            ]

    def __call__(self):
        """Perform operations."""
        self.report_summary()
        self.report_messages()

    def report_messages(self):
        info_messages = []
        warning_messages = []
        for prospector_message in self.report["messages"]:
            source = prospector_message["source"]
            code = prospector_message["code"]
            message = prospector_message["message"]
            filename = normpath(prospector_message["location"]["path"])
            line = prospector_message["location"]["line"]
            col = prospector_message["location"]["character"]
            github_message = f"prospector[{source}:{code}]: {message}"
            if self.modified_files is None or filename in self.modified_files:
                warning_messages.append(
                    f"::warning file={filename},line={line},col={col}::{github_message}"
                )
            else:
                info_messages.append(
                    f"::info file={filename},line={line},col={col}::{github_message}"
                )
        for warning_message in warning_messages:
            print(warning_message)
        for info_message in info_messages:
            print(info_message)

    def report_summary(self):
        summary = self.report["summary"]
        tools = str(summary["tools"]).strip("[]").replace("'", "")
        message_count = summary["message_count"]
        github_message = (
            f"prospector reported {message_count} total messages from tools: {tools}"
        )
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
            "infile", type=cls.input_path_arg(), help="Input prospector JSON file"
        )

        return parser


if __name__ == "__main__":
    ProspectorReporter.main()
