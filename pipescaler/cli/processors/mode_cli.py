#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Command line interface for ModeProcessor."""
from __future__ import annotations

from argparse import ArgumentParser, _SubParsersAction
from typing import Type, Union

from pipescaler.core.cli import ProcessorCli
from pipescaler.core.image import Processor
from pipescaler.image.processors import ModeProcessor


class ModeCli(ProcessorCli):
    """Command line interface for ModeProcessor."""

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

        required = cls.get_required_arguments_group(parser)
        required.add_argument(
            "--mode",
            required=True,
            type=cls.str_arg(options=cls.processor.inputs["input"]),
            help=f"image mode ({cls.processor.inputs['input']})",
        )

        optional = cls.get_optional_arguments_group(parser)
        optional.add_argument(
            "--background_color",
            default="#000000",
            type=str,
            help="background color of output image; only relevant if input image is "
            "RGBA or LA (default: %(default)s)",
        )

    @classmethod
    @property
    def processor(cls) -> Type[Processor]:
        """Type of processor wrapped by command line interface."""
        return ModeProcessor


if __name__ == "__main__":
    ModeCli.main()
