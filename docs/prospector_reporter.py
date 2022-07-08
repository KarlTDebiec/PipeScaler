#!/usr/bin/env python
#  Copyright (C) 2020-2022. Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Prints prospector output formatted for consumption by GitHub."""
import json
from argparse import ArgumentParser, FileType, RawDescriptionHelpFormatter
from dataclasses import dataclass
from inspect import cleandoc
from io import TextIOWrapper
from pathlib import Path

package_root = Path(__file__).absolute().parent.parent


@dataclass
class Message:
    source: str
    level: str
    file_path: Path
    line: int
    kind: str
    message: str


class ProspectorReporter:
    """Prints prospector output formatted for consumption by GitHub."""

    def __init__(self, infile: TextIOWrapper, modified_files_infile: TextIOWrapper):
        """Validate configuration and initialize.

        Arguments:
            infile: Input prospector json output
            modified_files_infile: Input list of modified files
        """
        self.messages = self.parse_prospector(infile)
        self.changed_files = self.parse_changed_files(modified_files_infile)

    def __call__(self) -> None:
        """Print messages formatted for consumption by GitHub."""
        for message in self.messages:
            if message.file_path in self.changed_files:
                print(
                    f"::{message.level} "
                    f"file={message.file_path},"
                    f"line={message.line}::"
                    f"{message.source}[{message.kind}] : "
                    f"{message.message}"
                )

    @classmethod
    def argparser(cls) -> ArgumentParser:
        """Get argument parser."""
        parser = ArgumentParser(
            description=str(cleandoc(cls.__doc__) if cls.__doc__ is not None else ""),
            formatter_class=RawDescriptionHelpFormatter,
        )
        parser.add_argument(
            "infile",
            type=FileType("r", encoding="UTF-8"),
            help="prospector output file",
        )
        parser.add_argument(
            "modified_files_infile",
            type=FileType("r", encoding="UTF-8"),
            help="Modified files file",
        )

        return parser

    @classmethod
    def main(cls) -> None:
        """Execute from command line."""
        parser = cls.argparser()
        kwargs = vars(parser.parse_args())
        reporter = cls(**kwargs)
        reporter()

    @classmethod
    def parse_prospector(cls, infile: TextIOWrapper) -> list[Message]:
        """Parse prospector input file.

        Arguments:
            infile: Input file
        """
        messages = []
        report = json.load(infile)

        for match in report["messages"]:
            file_path = (
                package_root.joinpath(Path(match["location"]["path"]))
                .resolve()
                .relative_to(package_root)
            )
            messages.append(
                Message(
                    source="prospector",
                    level="warning",
                    file_path=file_path,
                    line=int(match["location"]["line"]),
                    kind=f"{match['source']}:{match['code']}",
                    message=match["message"],
                )
            )

        return messages

    @staticmethod
    def parse_changed_files(infile: TextIOWrapper) -> list[Path]:
        """Parse changed files input file.

        Arguments:
            infile: Input file
        """
        text = infile.read()
        return list(map(Path, text.strip("[]\n").split(",")))


if __name__ == "__main__":
    ProspectorReporter.main()
