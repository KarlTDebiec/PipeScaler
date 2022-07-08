#!/usr/bin/env python
#  Copyright (C) 2020-2022. Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Prints mypy output formatted for consumption by GitHub."""
import re
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from inspect import cleandoc
from os.path import expandvars, normpath
from pathlib import Path
from typing import Union

package_root = Path(__file__).absolute().parent.parent


class MypyReporter:
    """Prints mypy output formatted for consumption by GitHub."""

    message_regex = re.compile(
        r"^"
        r"(?P<file_path>([A-Z]:)?[^:]+)"
        r":"
        r"(?P<line>\d+)"
        r":\s*"
        r"(?P<kind>[^:]+)"
        r":\s*"
        r"(?P<message>[^\n]+)"
        r"$"
    )

    def __init__(
        self,
        input_file_path: Union[str, Path],
        changed_files_input_path: Union[str, Path],
    ):
        """Validate configuration and initialize.

        Arguments:
            input_file_path: Path to input file
        """
        self.messages: list[dict[str, Union[int, str, Path]]] = []
        input_file_path = Path(expandvars(input_file_path)).resolve().absolute()
        self.parse_mypy(input_file_path)

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

    def parse_mypy(self, input_file_path: Path) -> None:
        """Parse mypy input file.

        Arguments:
            input_file_path: Path to input file
        """
        with open(input_file_path, "r", encoding="utf-8") as input_file:
            input_text = input_file.read()

        last_error_index = None
        for match in [m.groupdict() for m in self.message_regex.finditer(input_text)]:
            file_path = (
                package_root.joinpath(Path(match["file_path"]))
                .resolve()
                .relative_to(package_root)
            )
            if match["kind"] == "error":
                self.messages.append(
                    {
                        "level": "warning",
                        "file_path": file_path,
                        "line": int(match["line"]),
                        "kind": match["kind"],
                        "message": match["message"],
                    }
                )
                last_error_index = len(self.messages) - 1
            elif match["kind"] == "note":
                last_error = self.messages[last_error_index]
                if (
                    last_error["file_path"] == match["file_path"]
                    and last_error["line"] == match["line"]
                ):
                    last_error["message"] += "\n" + match["message"]
                self.messages[last_error_index]["message"] += f"\n{match['message']}"

    def print_messages(self) -> None:
        """Print messages formatted for consumption by GitHub."""
        for message in self.messages:
            print(
                f"::{message['level']} "
                f"file={message['file_path']},"
                f"line={message['line']}::"
                f"mypy[{message['kind']}] : "
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
            help="Path to mypy output file",
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
    MypyReporter.main()
