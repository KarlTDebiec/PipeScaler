#!/usr/bin/env python
#  Copyright (C) 2020-2022. Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Prints pytest output formatted for consumption by GitHub."""
import re
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from inspect import cleandoc
from pathlib import Path
from typing import Union

package_root = Path(__file__).absolute().parent.parent


class PytestReporter:
    """Prints pytest output formatted for consumption by GitHub."""

    warning_section_regex = re.compile(
        r"[\S\s]*"
        r"(?P<header>^=+ warnings summary =+$)"
        r"(?P<body>[\S\s]*)"
        r"(?P<footer>^-- Docs: "
        r"https://docs.pytest.org/en/stable/how-to/capture-warnings.html$)"
        r"[\S\s]*",
        re.MULTILINE,
    )
    warning_regex = re.compile(
        r"^\s*"
        r"(?P<file_path>([A-Z]:)?[^:]+)"
        r":"
        r"(?P<line>\d+)"
        r":"
        r"(?P<warning>[^:]+)"
        r":"
        r"(?P<message>[^\n]+)"
        r"\n"
        r"(?P<code>[^\n]+)",
        re.MULTILINE,
    )

    def __init__(
        self,
        pytest_infile: Union[str, Path],
    ):
        """Validate configuration and initialize.

        Arguments:
            pytest_infile: Path to pytest output
        """
        pytest_infile = Path(pytest_infile).absolute()
        self.messages = self.parse_messages(pytest_infile)

    @classmethod
    def parse_messages(cls, infile: Path) -> list[dict[str, Union[int, str, Path]]]:
        """Parse pytest output infile for messages.

        Arguments:
            infile: Path to pytest output
        Returns:
            List of warning messages
        """
        messages = []

        with open(infile, "r", encoding="utf-8") as infile:
            full_text = infile.read()

        section_match = cls.warning_section_regex.match(full_text)
        if section_match is None:
            return messages

        body = section_match.group("body")
        for warning_match in [m.groupdict() for m in cls.warning_regex.finditer(body)]:
            file_path = Path(warning_match["file_path"])
            if not file_path.is_relative_to(package_root):
                continue
            if file_path.relative_to(package_root).parts[0] == ".venv":
                continue
            messages.append(
                {
                    "file_path": file_path,
                    "line": int(warning_match["line"]),
                    "warning": warning_match["warning"].strip(),
                    "message": warning_match["message"].strip(),
                    "code": warning_match["code"].strip(),
                }
            )

        return messages

    @classmethod
    def print_messages(cls, messages: list[dict[str, Union[int, str, Path]]]):
        """Print messages formatted for consumption by GitHub.

        Arguments:
            messages: Messages to print
        """
        for message in messages:
            print(
                f"::warning "
                f"file={message['file_path'].relative_to(package_root)},"
                f"line={message['line']}::"
                f"pytest[{message['warning']}] : "
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
        reporter.print_messages(reporter.messages)


if __name__ == "__main__":
    PytestReporter.main()
