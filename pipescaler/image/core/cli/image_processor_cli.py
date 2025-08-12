#!/usr/bin/env python
#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for ImageProcessor command-line interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod
from argparse import ArgumentParser
from inspect import cleandoc
from logging import info
from typing import Any

from PIL import Image

from pipescaler.common import CommandLineInterface
from pipescaler.common.argument_parsing import input_file_arg, output_file_arg
from pipescaler.image.core.operators import ImageProcessor


class ImageProcessorCli(CommandLineInterface, ABC):
    """Abstract base class for ImageProcessor command-line interfaces."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: Nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        parser.add_argument(
            "input_file",
            type=input_file_arg(),
            help="input file",
        )
        parser.add_argument(
            "output_file",
            type=output_file_arg(),
            help="output file",
        )

    @classmethod
    def description(cls) -> str:
        """Long description of this tool displayed below usage."""
        return cleandoc(str(cls.processor().__doc__)) if cls.processor().__doc__ else ""

    @classmethod
    def _main(cls, **kwargs: Any):
        """Execute with provided keyword arguments."""
        input_path = kwargs.pop("input_file")
        output_path = kwargs.pop("output_file")
        processor_cls = cls.processor()
        processor = processor_cls(**kwargs)
        with Image.open(input_path) as input_img:
            output_img = processor(input_img)
            output_img.save(output_path)
            info(f"{cls}: '{output_path}' saved")

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser."""
        return cls.__name__.removesuffix("Cli").lower()

    @classmethod
    @abstractmethod
    def processor(cls) -> type[ImageProcessor]:
        """Type of processor wrapped by command-line interface."""
        raise NotImplementedError()
