#!/usr/bin/env python
#  Copyright (C) 2020-2022. Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Prints pytest output formatted for consumption by GitHub."""
import re
import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from inspect import cleandoc
from pathlib import Path
from typing import Union

package_root = Path(__file__).absolute().parent.parent


class PytestReporter:
    """Prints pytest output formatted for consumption by GitHub."""

    header_regexes = {
        "start": re.compile(r"^=+ test session starts =+$", re.MULTILINE),
        "failures": re.compile(r"^=+ FAILURES =+$", re.MULTILINE),
        "warnings": re.compile(r"^=+ warnings summary =+$", re.MULTILINE),
        "coverage": re.compile(r"^-+ coverage.* -+$", re.MULTILINE),
        "summary": re.compile(r"^=+ short test summary info =+$", re.MULTILINE),
    }
    failure_regex = re.compile(
        r"^E\s+(?P<kind>[^:\n]+):\s+(?P<message>[^\n]+)$"
        r"\n^\s*$\n"
        r"^(?P<file_path>([A-Z]:)?[^:]+):(?P<line>\d+):\s+(?P<kind2>[^:\n]+$)",
        re.MULTILINE,
    )
    warning_regex = re.compile(
        r"^\s*"
        r"(?P<file_path>([A-Z]:)?[^:]+)"
        r":"
        r"(?P<line>\d+)"
        r":"
        r"(?P<kind>[^:]+)"
        r":"
        r"(?P<message>[^\n]+)"
        r"\n"
        r"(?P<code>[^\n]+)",
        re.MULTILINE,
    )

    def __init__(self, input_file_path: Union[str, Path]):
        """Validate configuration and initialize.

        Arguments:
            input_file_path: Path to input file
        """
        self.messages = []
        self.return_code = 0
        self.parse(Path(input_file_path).absolute())

    def parse(self, input_file_path: Path) -> None:
        """Parse input file.

        Arguments:
            input_file_path: Path to input file
        """
        with open(input_file_path, "r", encoding="utf-8") as input_file:
            input_text = input_file.read()

        # Determine which section headers are present
        headers = []
        for section, regex in self.header_regexes.items():
            match = regex.search(input_text)
            if match:
                headers.append(
                    {
                        "name": section,
                        "start": match.start(),
                        "end": match.end(),
                    }
                )

        # Determine section body locations
        bodies = {}
        for i in range(1, len(headers)):
            bodies[headers[i - 1]["name"]] = {
                "start": headers[i - 1]["end"],
                "end": headers[i]["start"],
            }
        bodies[headers[i]["name"]] = {
            "start": headers[i]["end"],
            "end": len(input_text),
        }

        # Parse sections
        for section, location in bodies.items():
            if section == "failures":
                self.parse_failures_section(
                    input_text[location["start"] : location["end"]]
                )
            elif section == "warnings":
                self.parse_warnings_section(
                    input_text[location["start"] : location["end"]]
                )

    def parse_failures_section(self, body: str) -> None:
        """Parse failures section of pytest output.

        Arguments:
            body: Body of failures section
        """
        for match in [m.groupdict() for m in self.failure_regex.finditer(body)]:
            self.return_code = 1
            file_path = Path(match["file_path"])
            file_path = (
                package_root.joinpath("test", file_path)
                .resolve()
                .relative_to(package_root)
            )
            self.messages.append(
                {
                    "level": "error",
                    "file_path": file_path,
                    "line": int(match["line"]),
                    "kind": match["kind"],
                    "message": match["message"],
                }
            )

    def parse_warnings_section(self, body: str) -> None:
        """Parse warnings section of pytest output.

        Arguments:
            body: Body of warnings section
        """
        for match in [m.groupdict() for m in self.warning_regex.finditer(body)]:
            file_path = Path(match["file_path"])
            if not file_path.is_relative_to(package_root):
                continue
            if file_path.relative_to(package_root).parts[0] == ".venv":
                continue
            file_path = file_path.relative_to(package_root)
            self.messages.append(
                {
                    "level": "warning",
                    "file_path": file_path,
                    "line": int(match["line"]),
                    "kind": match["kind"].strip(),
                    "message": match["message"].strip(),
                }
            )

    def print_messages(self) -> None:
        """Print messages formatted for consumption by GitHub."""
        for message in self.messages:
            print(
                f"::{message['level']} "
                f"file={message['file_path']},"
                f"line={message['line']}::"
                f"pytest[{message['kind']}] : "
                f"{message['message']}"
            )

    @classmethod
    def argparser(cls) -> ArgumentParser:
        """Get argument parser."""
        parser = ArgumentParser(
            description=str(cleandoc(cls.__doc__)),
            formatter_class=RawDescriptionHelpFormatter,
        )
        parser.add_argument(
            "pytest_infile",
            type=str,
            help="Input pytest output file",
        )

        return parser

    @classmethod
    def main(cls) -> None:
        """Execute from command line."""
        parser = cls.argparser()
        kwargs = vars(parser.parse_args())
        reporter = cls(**kwargs)
        reporter.print_messages()
        sys.exit(reporter.return_code)


if __name__ == "__main__":
    PytestReporter.main()
