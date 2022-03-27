#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for PipeScaler."""
from __future__ import annotations

from argparse import ArgumentParser
from typing import Any

from pipescaler.cl.process_cl import ProcessCL
from pipescaler.cl.run_cl import RunCL
from pipescaler.cl.utility_cl import UtilityCL
from pipescaler.common import CommandLineTool


class PipeScalerCL(CommandLineTool):
    """Command-line interface for PipeScaler."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def __call__(self) -> None:
        pass

    @classmethod
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """Construct argument parser.

        Arguments:
            kwargs: Additional keyword arguments
        Returns:
            parser: Argument parser
        """
        parser = super().construct_argparser(description=cls.description, **kwargs)

        subparsers = parser.add_subparsers()
        ProcessCL.construct_argparser(parser=subparsers, name="run")
        RunCL.construct_argparser(parser=subparsers, name="run")
        UtilityCL.construct_argparser(parser=subparsers, name="run")

        return parser


if __name__ == "__main__":
    PipeScalerCL.main()
