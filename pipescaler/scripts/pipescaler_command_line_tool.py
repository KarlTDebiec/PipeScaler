#!/usr/bin/env python
#   pipescaler/scripts/pipescaler.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""PipeScaler"""
from __future__ import annotations

from argparse import ArgumentParser
from inspect import cleandoc
from typing import Any

from pipescaler.common import CommandLineTool
from pipescaler.scripts.apng_creator import ApngCreator
from pipescaler.scripts.file_scanner import FileScanner
from pipescaler.scripts.pipe_runner import PipeRunner
from pipescaler.scripts.pipescaler_host import PipescalerHost


class PipeScalerCommandLineTool(CommandLineTool):
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
        description = kwargs.pop(
            "description", cleandoc(cls.__doc__) if cls.__doc__ is not None else ""
        )
        parser = super().construct_argparser(description=description, **kwargs)

        subparsers = parser.add_subparsers()
        ApngCreator.construct_argparser(parser=subparsers)
        FileScanner.construct_argparser(parser=subparsers, name="scan")
        PipeRunner.construct_argparser(parser=subparsers)
        PipescalerHost.construct_argparser(parser=subparsers)
        # ScaledImageIdentifier.construct_argparser(parser=subparsers)
        return parser


if __name__ == "__main__":
    PipeScalerCommandLineTool.main()
