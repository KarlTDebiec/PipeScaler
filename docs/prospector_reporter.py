#!/usr/bin/env python
#  Copyright (C) 2020-2022. Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Prints prospector output formatted for consumption by GitHub."""
import json
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from inspect import cleandoc
from os.path import expandvars, normpath
from pathlib import Path
from typing import Union

package_root = Path(__file__).absolute().parent.parent


class ProspectorReporter:
    """Prints prospector output formatted for consumption by GitHub."""

    def __init__(
        self,
        input_file_path: Union[str, Path],
        changed_files_input_path: Union[str, Path],
    ):
        """Validate configuration and initialize.

        Arguments:
            prospector_infile: Path to prospector json output
            modified_files_infile: Path to list of modified files
        """
        self.messages = []
        input_file_path = Path(expandvars(input_file_path)).resolve().absolute()
        self.parse_prospector(input_file_path)

        self.changed_files = []
        changed_files_input_path = (
            Path(expandvars(changed_files_input_path)).resolve().absolute()
        )
        self.parse_changed_files(changed_files_input_path)

    def parse_changed_files(self, input_file_path: Path) -> None:
        """Parse changed files input file.

        Arguments:
            input_file_path: Path to input file
        """
        with open(input_file_path, "r", encoding="utf-8") as infile:
            self.changed_files = list(
                map(normpath, infile.read().strip("[]\n").split(","))
            )

    def parse_prospector(self, input_file_path: Path) -> None:
        """Parse prospector input file.

        Arguments:
            input_file_path: Path to input file
        """
        with open(input_file_path, "r", encoding="utf-8") as infile:
            report = json.load(infile)

        for match in report["messages"]:
            file_path = (
                package_root.joinpath(Path(match["location"]["path"]))
                .resolve()
                .relative_to(package_root)
            )
            self.messages.append(
                {
                    "level": "warning",
                    "file_path": file_path,
                    "line": int(match["location"]["line"]),
                    "kind": f"{match['source']}:{match['code']}",
                    "message": match["message"],
                }
            )

    def print_messages(self) -> None:
        """Print messages formatted for consumption by GitHub."""
        for message in self.messages:
            if message["file_path"] in self.changed_files:
                print(
                    f"::{message['level']} "
                    f"file={message['file_path']},"
                    f"line={message['line']}::"
                    f"prospector[{message['kind']}] : "
                    f"{message['message']}"
                )

    @classmethod
    def argparser(cls) -> ArgumentParser:
        """Get argument parser."""
        parser = ArgumentParser(
            description=str(cleandoc(cls.__doc__) if cls.__doc__ is not None else ""),
            formatter_class=RawDescriptionHelpFormatter,
        )
        parser.add_argument(
            "input_file_path",
            type=str,
            help="Path to prospector output file",
        )
        parser.add_argument(
            "changed_files_input_path",
            type=str,
            help="Path to changed files input file",
        )

        return parser

    @classmethod
    def main(cls) -> None:
        """Execute from command line."""
        parser = cls.argparser()
        kwargs = vars(parser.parse_args())
        reporter = cls(**kwargs)
        reporter.print_messages()


if __name__ == "__main__":
    ProspectorReporter.main()
