#!/usr/bin/env python
#  Copyright (C) 2020-2022. Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Prints pydocstyle output formatted for consumption by GitHub."""
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from inspect import cleandoc
from itertools import zip_longest
from os.path import normpath
from pathlib import Path
from typing import Union


class PydocstyleReporter:
    """Prints pydocstyle output formatted for consumption by GitHub."""

    def __init__(
        self,
        pydocstyle_infile: Union[str, Path],
        modified_files_infile: Union[str, Path],
    ):
        """Validate configuration and initialize.

        Arguments:
            pydocstyle_infile: Path to pydocstyle json output
            modified_files_infile: Path to list of modified files
        """
        self.messages = []
        pydocstyle_infile = Path(pydocstyle_infile).absolute()
        with open(pydocstyle_infile, "r", encoding="utf-8") as infile:
            for line, issue in zip_longest(*[infile] * 2):
                file, line = line.split()[0].split(":")
                code, message = issue.strip().split(": ")
                self.messages.append(
                    {"file": file, "line": line, "code": code, "message": message}
                )

        modified_files_infile = Path(modified_files_infile).absolute()
        with open(modified_files_infile, "r", encoding="utf-8") as infile:
            self.modified_files = list(
                map(normpath, infile.read().strip("[]\n").split(","))
            )

    def print_messages(self):
        """Print messages formatted for consumption by GitHub."""
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

    def print_summary(self):
        """Print summary formatted for consumption by GitHub."""
        message_count = len(self.messages)
        github_message = f"pydocstyle reported {message_count} total messages"
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
            "pydocstyle_infile",
            type=str,
            help="Input pydocstyle output file",
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
    PydocstyleReporter.main()
