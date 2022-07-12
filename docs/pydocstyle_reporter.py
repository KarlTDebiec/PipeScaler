#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Prints pydocstyle output formatted for consumption by GitHub."""
from argparse import ArgumentParser, FileType, RawDescriptionHelpFormatter
from dataclasses import dataclass
from inspect import cleandoc
from io import TextIOWrapper
from itertools import zip_longest
from pathlib import Path

package_root = Path(__file__).absolute().parent.parent


@dataclass
class Annotation:
    """Annotation data for GitHub."""

    source: str
    level: str
    file_path: Path
    line: int
    kind: str
    message: str


class PydocstyleReporter:
    """Prints pydocstyle output formatted for consumption by GitHub."""

    def __init__(self, infile: TextIOWrapper, modified_files_infile: TextIOWrapper):
        """Validate configuration and initialize.

        Arguments:
            infile: Input file
            modified_files_infile: List of modified files input file
        """
        self.annotations = self.parse_pydocstyle(infile)
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
            help="pydocstyle output file",
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
    def parse_pydocstyle(cls, infile: TextIOWrapper) -> list[Annotation]:
        """Parse pydocstyle input file.

        Arguments:
            infile: Input file
        Returns:
            Annotations
        """
        annotations = []
        for line, issue in zip_longest(*[infile] * 2):
            file_path, line = line.split()[0].split(":")
            file_path = (
                package_root.joinpath(Path(file_path))
                .resolve()
                .relative_to(package_root)
            )
            line = int(line)
            kind, message = issue.strip().split(": ")
            annotations.append(
                Annotation(
                    source="pydocstyle",
                    level="warning",
                    file_path=file_path,
                    line=line,
                    kind=kind,
                    message=message,
                )
            )

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
    PydocstyleReporter.main()
