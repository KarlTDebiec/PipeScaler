#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""PipeScaler"""
from __future__ import annotations

from argparse import ArgumentParser, _SubParsersAction
from inspect import cleandoc
from typing import Any

from pipescaler.common import CommandLineTool
from pipescaler.processors import (
    AppleScriptProcessor,
    AutomatorProcessor,
    CropProcessor,
    ESRGANProcessor,
    ExpandProcessor,
    GigapixelAiProcessor,
    HeightToNormalProcessor,
    ModeProcessor,
    PngquantProcessor,
    PotraceProcessor,
    ResizeProcessor,
    SharpenProcessor,
    SideChannelProcessor,
    SolidColorProcessor,
    TexconvProcessor,
    ThresholdProcessor,
    WaifuExternalProcessor,
    WaifuProcessor,
    WebProcessor,
    XbrzProcessor,
)
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
        parser = super().construct_argparser(description=cls.description, **kwargs)

        subparsers = parser.add_subparsers()
        FileScanner.construct_argparser(parser=subparsers, name="scan")
        PipeRunner.construct_argparser(parser=subparsers, name="run")
        PipescalerHost.construct_argparser(parser=subparsers, name="host")
        cls.construct_processor_subparser(subparsers)
        cls.construct_utility_subparser(subparsers)

        return parser

    @classmethod
    def construct_processor_subparser(cls, subparsers: _SubParsersAction) -> None:
        processor_subparser = subparsers.add_parser(name="process", help="Processors")
        processor_subparsers = processor_subparser.add_subparsers()

        AppleScriptProcessor.construct_argparser(parser=processor_subparsers)
        AutomatorProcessor.construct_argparser(parser=processor_subparsers)
        CropProcessor.construct_argparser(parser=processor_subparsers)
        ESRGANProcessor.construct_argparser(parser=processor_subparsers)
        ExpandProcessor.construct_argparser(parser=processor_subparsers)
        GigapixelAiProcessor.construct_argparser(parser=processor_subparsers)
        HeightToNormalProcessor.construct_argparser(parser=processor_subparsers)
        ModeProcessor.construct_argparser(parser=processor_subparsers)
        PngquantProcessor.construct_argparser(parser=processor_subparsers)
        PotraceProcessor.construct_argparser(parser=processor_subparsers)
        ResizeProcessor.construct_argparser(parser=processor_subparsers)
        SharpenProcessor.construct_argparser(parser=processor_subparsers)
        SideChannelProcessor.construct_argparser(parser=processor_subparsers)
        SolidColorProcessor.construct_argparser(parser=processor_subparsers)
        TexconvProcessor.construct_argparser(parser=processor_subparsers)
        ThresholdProcessor.construct_argparser(parser=processor_subparsers)
        WaifuExternalProcessor.construct_argparser(parser=processor_subparsers)
        WaifuProcessor.construct_argparser(parser=processor_subparsers)
        WebProcessor.construct_argparser(parser=processor_subparsers)
        XbrzProcessor.construct_argparser(parser=processor_subparsers)

    @classmethod
    def construct_utility_subparser(clscls, subparsers: _SubParsersAction) -> None:
        utility_subparser = subparsers.add_parser(name="utility", help="Utilities")
        utility_subparsers = utility_subparser.add_subparsers()

        ApngCreator.construct_argparser(parser=utility_subparsers)
        # ScaledImageIdentifier.construct_argparser(parser=utility_subparsers)


if __name__ == "__main__":
    PipeScalerCommandLineTool.main()
