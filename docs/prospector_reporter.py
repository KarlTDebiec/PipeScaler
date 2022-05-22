#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Prints prospector results formatted for consumption by GitHub."""
import json
from argparse import ArgumentParser, _SubParsersAction
from os.path import normpath
from typing import Any, Union

from pipescaler.common import CommandLineInterface, validate_input_file


class ProspectorReporter(CommandLineInterface):
    """Prints prospector results formatted for consumption by GitHub."""

    def __init__(
        self,
        prospector_infile: str,
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

        with open(validate_input_file(prospector_infile)) as infile:
            self.report = json.load(infile)

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
        for prospector_message in self.report["messages"]:
            source = prospector_message["source"]
            code = prospector_message["code"]
            message = prospector_message["message"]
            filename = normpath(prospector_message["location"]["path"])
            line = prospector_message["location"]["line"]
            col = prospector_message["location"]["character"]
            github_message = f"prospector[{source}:{code}]: {message}"
            if filename in self.modified_files:
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
        print(f"::info::{github_message}")

    @classmethod
    def add_arguments_to_argparser(
        cls,
        parser: Union[ArgumentParser, _SubParsersAction],
    ) -> None:
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: Nascent argument parser
        """
        parser.add_argument(
            "prospector_infile",
            type=cls.input_path_arg(),
            help="Input prospector output file in JSON format",
        )
        parser.add_argument(
            "modified_files_infile",
            type=cls.input_path_arg(),
            help="Input list of added or modified files",
        )

    @classmethod
    def execute(cls, **kwargs: Any) -> None:
        """Execute with provided keyword arguments.

        Args:
            **kwargs: Command-line arguments
        """
        cls(**kwargs)()


if __name__ == "__main__":
    ProspectorReporter.main()
