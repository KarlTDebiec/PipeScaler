#!/usr/bin/env python
#  Copyright (C) 2020-2022. Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Prints prospector output formatted for consumption by GitHub."""
import json
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from inspect import cleandoc
from os.path import normpath
from pathlib import Path
from typing import Union


class ProspectorReporter:
    """Prints prospector output formatted for consumption by GitHub."""

    def __init__(
        self,
        prospector_infile: Union[str, Path],
        modified_files_infile: Union[str, Path],
    ):
        """Validate configuration and initialize.

        Arguments:
            prospector_infile: Path to prospector json output
            modified_files_infile: Path to list of modified files
        """
        prospector_infile = Path(prospector_infile).absolute()
        with open(prospector_infile, "r", encoding="utf-8") as infile:
            self.report = json.load(infile)

        modified_files_infile = Path(modified_files_infile).absolute()
        with open(modified_files_infile, "r", encoding="utf-8") as infile:
            self.modified_files = list(
                map(normpath, infile.read().strip("[]\n").split(","))
            )

    def print_messages(self):
        """Print messages formatted for consumption by GitHub."""
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

    def print_summary(self):
        """Print summary formatted for consumption by GitHub."""
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
    def argparser(cls) -> ArgumentParser:
        """Get argument parser."""
        parser = ArgumentParser(
            description=str(cleandoc(cls.__doc__)),
            formatter_class=RawDescriptionHelpFormatter,
        )
        parser.add_argument(
            "prospector_infile",
            type=str,
            help="Input prospector output file in JSON format",
        )
        parser.add_argument(
            "modified_files_infile",
            type=str,
            help="Input list of added or modified files",
        )

        return parser

    @classmethod
    def main(cls) -> None:
        """Execute from command line."""
        parser = cls.argparser()
        kwargs = vars(parser.parse_args())
        reporter = cls(**kwargs)
        reporter.print_summary()
        reporter.print_messages()


if __name__ == "__main__":
    ProspectorReporter.main()
