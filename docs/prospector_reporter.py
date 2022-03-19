#!/usr/bin/env python
#   prospector_reporter.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Prints prospector results formatted for consumption by GitHub."""
import json
from argparse import ArgumentParser
from inspect import cleandoc
from typing import Any

from pipescaler.common import CommandLineTool, validate_input_file


class ProspectorReporter(CommandLineTool):
    """Prints prospector results formatted for consumption by GitHub."""

    def __init__(self, infile, **kwargs):
        """Validate and store static configuration.

        Arguments:
            infile: Path to input prospector json output
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        self.infile = validate_input_file(infile)

    def __call__(self):
        """Perform operations."""
        with open(self.infile) as file:
            report = json.load(file)

        for prospector_message in report["messages"]:
            source = prospector_message["source"]
            code = prospector_message["code"]
            message = prospector_message["message"]
            file = prospector_message["location"]["path"]
            line = prospector_message["location"]["line"]
            col = prospector_message["location"]["character"]
            github_message = f"prospector[{source}:{code}]: {message}"
            print(f"::warning file={file},line={line},col={col}::{github_message}")

    @classmethod
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """Construct argument parser.

        Arguments:
            **kwargs: Additional keyword arguments
        Returns:
            parser: Argument parser
        """
        description = kwargs.pop(
            "description", cleandoc(cls.__doc__) if cls.__doc__ is not None else ""
        )
        parser = super().construct_argparser(description=description, **kwargs)

        parser.add_argument(
            "infile", type=cls.input_path_arg(), help="Input prospector JSON file"
        )

        return parser


if __name__ == "__main__":
    ProspectorReporter.main()
