#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Prints mypy output formatted for consumption by GitHub."""
import re
from argparse import ArgumentParser, FileType, RawDescriptionHelpFormatter
from dataclasses import dataclass
from inspect import cleandoc
from io import TextIOWrapper
from pathlib import Path

package_root = Path(__file__).resolve().parent.parent


@dataclass
class Annotation:
    """Annotation data for GitHub."""

    source: str
    level: str
    file_path: Path
    line: int
    kind: str
    message: str


class MypyReporter:
    """Prints mypy output formatted for consumption by GitHub."""

    annotation_regex = re.compile(
        r"\s*"
        r"(?P<file_path>([A-Z]:)?[^:]+)"
        r":"
        r"(?P<line>\d+)"
        r":\s*"
        r"(?P<kind>[^:]+)"
        r":\s*"
        r"(?P<message>[^\n]+)"
    )

    def __init__(self, infile: TextIOWrapper, modified_files_infile: TextIOWrapper):
        """Validate configuration and initialize.

        Arguments:
            infile: Input file
            modified_files_infile: List of modified files input file
        """
        self.annotations = self.parse_mypy(infile)
        self.changed_files = self.parse_changed_files(modified_files_infile)

    def __call__(self) -> None:
        """Print annotations formatted for consumption by GitHub."""
        for annotation in self.annotations:
            if annotation.file_path in self.changed_files:
                print(
                    f"::{annotation.level} "
                    f"file={annotation.file_path},"
                    f"line={annotation.line}::"
                    f"{annotation.source}[{annotation.kind}] : "
                    f"{annotation.message}"
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
            help="mypy output file",
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
    def parse_mypy(cls, infile: TextIOWrapper) -> list[Annotation]:
        """Parse mypy input file.

        Arguments:
            infile: Input file
        Returns:
            Annotations
        """
        annotations: list[Annotation] = []
        text = infile.read()

        last_error_index = None
        for match in [m.groupdict() for m in cls.annotation_regex.finditer(text)]:
            file_path = Path(match["file_path"])
            file_path = (package_root / file_path).resolve().relative_to(package_root)
            if match["kind"] == "error":
                annotations.append(
                    Annotation(
                        source="mypy",
                        level="warning",
                        file_path=file_path,
                        line=int(match["line"]),
                        kind=match["kind"],
                        message=match["message"],
                    )
                )
                last_error_index = len(annotations) - 1
            elif match["kind"] == "note":
                if last_error_index is not None:
                    last_error = annotations[last_error_index]
                    if (
                        last_error.file_path == match["file_path"]
                        and last_error.line == match["line"]
                    ):
                        last_error.message += f"\n{match['message']}"

        return annotations

    @staticmethod
    def parse_changed_files(infile: TextIOWrapper) -> list[Path]:
        """Parse changed files input file.

        Arguments:
            infile: Input file
        """
        text = infile.read()
        return list(map(Path, text.strip("[]\n").split(",")))


if __name__ == "__main__":
    MypyReporter.main()
