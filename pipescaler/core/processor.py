#!/usr/bin/env python
#   pipescaler/processors/processor.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from abc import abstractmethod
from argparse import ArgumentParser
from os.path import isfile
from typing import Any, Generator, List, Optional, Union

from pipescaler.common import CLTool, validate_input_path, validate_output_path
from pipescaler.core import PipeImage
from pipescaler.core.stage import Stage


####################################### CLASSES ########################################
class Processor(Stage, CLTool):

    # region Builtins

    def __init__(
        self,
        suffix: Optional[str] = None,
        downstream_stages: Optional[Union[str, List[str]]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

        if suffix is not None:
            self.suffix = suffix
        else:
            self.suffix = self.name
        if isinstance(downstream_stages, str):
            downstream_stages = [downstream_stages]
        self.downstream_stages = downstream_stages

    def __call__(self, **kwargs: Any) -> Generator[PipeImage, PipeImage, None]:
        while True:
            image: PipeImage = (yield)
            if self.pipeline.verbosity >= 2:
                print(f"{self} processing: {image.name}")
            self.process_file_in_pipeline(image)
            # if self.downstream_stages is not None:
            #     for pipe in self.downstream_stages:
            #         self.pipeline.stages[pipe].send(outfile)

    # endregion

    # region Methods

    def process_file_in_pipeline(self, image: PipeImage) -> None:
        infile = validate_input_path(image.last)
        outfile = validate_output_path(self.pipeline.get_outfile(image, self.suffix))
        if not isfile(outfile):
            self.process_file(infile, outfile, verbosity=self.pipeline.verbosity)
        image.log(self.name, outfile)

    # endregion

    # region Class Methods

    @classmethod
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """
        Constructs argument parser.

        Args:
            kwargs (Any): Additional keyword arguments

        Returns:
            ArgumentParser: Argument parser
        """
        description = kwargs.get("description", __doc__.strip())
        parser = super().construct_argparser(description=description, **kwargs)

        # Input
        parser.add_argument("infile", type=cls.input_path_arg(), help="input file")

        # Output
        parser.add_argument("outfile", type=cls.output_path_arg(), help="output file")

        return parser

    @classmethod
    def main(cls) -> None:
        """Parses and validates arguments, passes them to process_file."""
        parser = cls.construct_argparser()
        kwargs = vars(parser.parse_args())
        cls.process_file_from_cl(**kwargs)

    @classmethod
    @abstractmethod
    def process_file(
        cls, infile: str, outfile: str, verbosity: int = 1, **kwargs: Any
    ) -> None:
        raise NotImplementedError()

    @classmethod
    def process_file_from_cl(cls, infile: str, outfile: str, **kwargs: Any) -> None:
        infile = validate_input_path(infile)
        outfile = validate_output_path(outfile)

        cls.process_file(infile, outfile, **kwargs)

    # endregion
