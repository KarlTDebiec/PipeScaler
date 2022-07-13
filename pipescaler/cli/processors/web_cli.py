#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Command line interface for WebProcessor."""
from __future__ import annotations

from argparse import ArgumentParser, _SubParsersAction
from typing import Type, Union

from pipescaler.core.cli import ProcessorCli
from pipescaler.core.image import Processor
from pipescaler.image.processors import WebProcessor


class WebCli(ProcessorCli):
    """Command line interface for WebProcessor."""

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
        required.add_argument("--url", type=str, help="URL to which to POST image")

    @classmethod
    def processor(cls) -> Type[Processor]:
        """Type of processor wrapped by command line interface."""
        return WebProcessor


if __name__ == "__main__":
    WebCli.main()
