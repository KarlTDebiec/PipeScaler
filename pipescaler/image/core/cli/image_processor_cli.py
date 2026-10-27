#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for ImageProcessor command-line interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod
from argparse import ArgumentParser
from inspect import cleandoc
from logging import info
from pathlib import Path

from PIL import Image

from pipescaler.common import CommandLineInterface
from pipescaler.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
    output_file_arg,
)
from pipescaler.image.core.operators import ImageProcessor

__all__ = ["ImageProcessorCli"]


class ImageProcessorCli(CommandLineInterface, ABC):
    """Abstract base class for ImageProcessor command-line interfaces."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: Nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        arg_groups = get_arg_groups_by_name(
            parser, "input arguments", "output arguments"
        )

        arg_groups["input arguments"].add_argument(
            "input_path",
            metavar="input_file",
            type=input_file_arg(),
            help="input file",
        )
        arg_groups["output arguments"].add_argument(
            "output_path",
            metavar="output_file",
            type=output_file_arg(),
            help="output file",
        )

    @classmethod
    def description(cls) -> str:
        """Long description of this tool displayed below usage.

        Returns:
            long description displayed in command help
        """
        return cleandoc(str(cls.processor().__doc__)) if cls.processor().__doc__ else ""

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            command name used by the argument parser
        """
        return cls.__name__.removesuffix("Cli").lower()

    @classmethod
    def process_image(
        cls, *, input_path: Path, output_path: Path, processor: ImageProcessor
    ):
        """Read, process, and save one image.

        Arguments:
            input_path: input image path
            output_path: output image path
            processor: configured image processor
        """
        with Image.open(input_path) as input_img:
            output_img = processor(input_img)
            output_img.save(output_path)
            info(f"{cls}: '{output_path}' saved")

    @classmethod
    @abstractmethod
    def processor(cls) -> type[ImageProcessor]:
        """Type of processor wrapped by command-line interface.

        Returns:
            image processor class invoked by this command
        """
        raise NotImplementedError()
