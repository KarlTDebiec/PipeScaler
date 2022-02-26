#!/usr/bin/env python
#   pipescaler/processors/web_processor.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""POSTs image to a defined URL, which responds with processed image"""
from __future__ import annotations

from argparse import ArgumentParser
from inspect import cleandoc
from logging import info
from os.path import basename
from typing import Any

import requests as requests

from pipescaler.core import Processor


class WebProcessor(Processor):
    """POSTs image to a defined URL, which responds with processed image"""

    def __init__(self, url: str, **kwargs: Any) -> None:
        """
        Validate and store static configuration

        Arguments:
            url: URL to which to POST image for processing
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Store configuration
        self.url = url

    def __call__(self, infile: str, outfile: str) -> None:
        """
        Read image from infile, process it, and save to outfile

        Arguments:
            infile: Input file path
            outfile: Output file path
        """
        # Read image
        with open(infile, "rb") as input_file:
            input_bytes = input_file.read()
        files = {"image": (basename(infile), input_bytes, "multipart/form-data")}

        # Process image
        with requests.Session() as session:
            response = session.post(self.url, files=files)
            if response.status_code != 200:
                raise ValueError()
        output_bytes = response.content

        # Write image
        with open(outfile, "wb") as output_file:
            output_file.write(output_bytes)
        info(f"{self}: '{outfile}' saved")

    @classmethod
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """
        Construct argument parser

        Arguments:
            **kwargs: Additional keyword arguments

        Returns:
            parser: Argument parser
        """
        description = kwargs.pop(
            "description", cleandoc(cls.__doc__) if cls.__doc__ is not None else ""
        )
        parser = super().construct_argparser(description=description, **kwargs)

        parser.add_argument("--url", type=str, help="URL to which to POST image")

        return parser


if __name__ == "__main__":
    WebProcessor.main()
