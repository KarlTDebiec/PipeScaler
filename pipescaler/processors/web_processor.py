#!/usr/bin/env python
#   pipescaler/processors/web_processor.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
from __future__ import annotations

from argparse import ArgumentParser
from inspect import cleandoc
from logging import info
from os.path import basename
from typing import Any

import requests as requests

from pipescaler.core import Processor


class WebProcessor(Processor):
    """POSTs image to a defined URL, which responds with processed image."""

    def __init__(self, url: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        # Store configuration
        self.url = url

    def process_file(self, infile: str, outfile: str) -> None:
        # Read image
        with open(infile, "rb") as input_file:
            files = {
                "image": (
                    basename(infile),
                    input_file.read(),
                    "multipart/form-data",
                    {"Expires": "0"},
                )
            }

        # Process image
        with requests.Session() as session:
            response = session.post(self.url, files=files)
            if response.status_code != 200:
                raise ValueError()

        # Write image
        with open(outfile, "wb") as output_file:
            output_file.write(response.content)
        info(f"{self}: '{outfile}' saved")

    @classmethod
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """
        Constructs argument parser.

        Args:
            kwargs (Any): Additional keyword arguments

        Returns:
            parser (ArgumentParser): Argument parser
        """
        description = kwargs.pop("description", cleandoc(cls.__doc__))
        parser = super().construct_argparser(description=description, **kwargs)

        parser.add_argument("--url", type=str, help="URL to which to POST image")

        return parser


if __name__ == "__main__":
    WebProcessor.main()
