#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for Processor command line interfaces."""
from __future__ import annotations

from abc import ABC, abstractmethod
from argparse import ArgumentParser, _SubParsersAction
from inspect import cleandoc
from typing import Any, Type, Union

from PIL import Image

from pipescaler.common import CommandLineInterface
from pipescaler.core.image.operators.processor import Processor


class ProcessorCli(CommandLineInterface, ABC):
    """Abstract base class for Processor command line interfaces."""

    @classmethod
    def add_arguments_to_argparser(
        cls,
        parser: Union[ArgumentParser, _SubParsersAction],
    ) -> None:
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: Nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        parser.add_argument("infile", type=cls.input_path_arg(), help="input file")
        parser.add_argument("outfile", type=cls.output_path_arg(), help="output file")

    @classmethod
    def execute(cls, **kwargs: Any) -> None:
        """Execute with provided keyword arguments.

        TODO: Decide on a consistent way for ProcessorCli and UtilityCli to manage
          arguments destined for __init__ and arguments destined for __call__

        Args:
            **kwargs: Command-line arguments
        """
        processor = cls.processor(**kwargs)
        infile = kwargs.pop("infile")
        outfile = kwargs.pop("outfile")
        with Image.open(infile) as input_image:
            output_image = processor(input_image)
            output_image.save(outfile)
            print(f"{cls}: '{outfile}' saved")

    @classmethod
    def main(cls) -> None:
        """Execute from command line."""
        parser = cls.construct_argparser()
        kwargs = vars(parser.parse_args())
        cls.execute(**kwargs)

    @classmethod
    @property
    def description(cls) -> str:
        """Long description of this tool displayed below usage."""
        if cls.processor.__doc__:
            return cleandoc(cls.processor.__doc__)
        return ""

    @classmethod
    @property
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser."""
        return cls.__name__.removesuffix("Cli").lower()

    @classmethod
    @property
    @abstractmethod
    def processor(cls) -> Type[Processor]:
        """Type of processor wrapped by command line interface."""
        raise NotImplementedError()
