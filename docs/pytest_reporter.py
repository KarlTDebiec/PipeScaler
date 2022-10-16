#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Prints pytest output formatted for consumption by GitHub."""
import re
import sys
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


@dataclass
class Section:
    """Section of input file."""

    name: str
    start: int
    end: int


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

    def __init__(self, infile: TextIOWrapper):
        """Validate configuration and initialize.

        Arguments:
            infile: Input file
        """
        self.annotations = self.parse_pytest(infile)

    def __call__(self) -> None:
        """Print annotations formatted for consumption by GitHub."""
        for annotation in self.annotations:
            print(
                f"::{annotation.level} "
                f"file={annotation.file_path},"
                f"line={annotation.line}::"
                f"{annotation.source}[{annotation.kind}] : "
                f"{annotation.message}"
            )

    def exit(self):
        """Exit, returning 1 if any tests failed and 0 otherwise."""
        for annotation in self.annotations:
            if annotation.level == "error":
                sys.exit(1)
        sys.exit(0)

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
            help="pytest output file",
        )

        return parser

    @classmethod
    def main(cls) -> None:
        """Execute from command line."""
        parser = cls.argparser()
        kwargs = vars(parser.parse_args())
        reporter = cls(**kwargs)
        reporter()
        reporter.exit()

    @classmethod
    def parse_pytest(cls, infile: TextIOWrapper) -> list[Annotation]:
        """Parse pytest input file.

        Arguments:
            infile: Input file
        Returns:
            Annotations
        """
        annotations = []
        text = infile.read()

        # Determine which section headers are present
        headers: list[Section] = []
        for section, regex in cls.header_regexes.items():
            match = regex.search(text)
            if match:
                headers.append(
                    Section(name=section, start=match.start(), end=match.end())
                )

        # Determine section body locations
        bodies: dict[str, Section] = {}
        for i in range(1, len(headers)):
            bodies[headers[i - 1].name] = Section(
                name=headers[i - 1].name,
                start=headers[i - 1].end,
                end=headers[i].start,
            )
        bodies[headers[i].name] = Section(
            name=headers[i].name,
            start=headers[i].end,
            end=len(text),
        )

        # Parse sections
        for section, location in bodies.items():
            if section == "failures":
                annotations.extend(
                    cls.parse_failures_section(text[location.start : location.end])
                )
            elif section == "warnings":
                annotations.extend(
                    cls.parse_warnings_section(text[location.start : location.end])
                )

        return annotations

    @classmethod
    def parse_failures_section(cls, body: str) -> list[Annotation]:
        """Parse failures section of pytest output.

        Arguments:
            body: Body of failures section
        Returns:
            Annotations
        """
        annotations = []
        for match in [m.groupdict() for m in cls.failure_regex.finditer(body)]:
            file_path = (
                package_root.joinpath("test", match["file_path"])
                .resolve()
                .relative_to(package_root)
            )
            annotations.append(
                Annotation(
                    source="pytest",
                    level="error",
                    file_path=file_path,
                    line=int(match["line"]),
                    kind=match["kind"].strip(),
                    message=match["message"].strip(),
                )
            )

        return annotations

    @classmethod
    def parse_warnings_section(cls, body: str) -> list[Annotation]:
        """Parse warnings section of pytest output.

        Arguments:
            body: Body of warnings section
        Returns:
            Annotations
        """
        annotations = []

        for match in [m.groupdict() for m in cls.warning_regex.finditer(body)]:
            file_path = Path(match["file_path"])
            if not file_path.is_relative_to(package_root):
                continue
            if file_path.relative_to(package_root).parts[0] == ".venv":
                continue
            file_path = file_path.relative_to(package_root)
            annotations.append(
                Annotation(
                    source="pytest",
                    level="warning",
                    file_path=file_path,
                    line=int(match["line"]),
                    kind=match["kind"].strip(),
                    message=match["message"].strip(),
                )
            )

        return annotations


if __name__ == "__main__":
    PytestReporter.main()
