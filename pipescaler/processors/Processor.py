#!/usr/bin/env python
#   pipescaler/processors/Processor.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
################################### MODULES ###################################
from __future__ import annotations

from abc import ABC, abstractmethod
from argparse import ArgumentError, ArgumentParser, RawDescriptionHelpFormatter
from os import R_OK, W_OK, access, getcwd, makedirs
from os.path import basename, dirname, expandvars, isdir, isfile, splitext
from shutil import copyfile, get_terminal_size
from textwrap import TextWrapper
from typing import Any, Iterator, List, Optional, Union

from pipescaler.Pipeline import Pipeline


################################### CLASSES ###################################
class Processor(ABC):
    desc: str = ""

    def __init__(self, pipeline: Pipeline,
                 downstream_pipes: Optional[Union[str, List[str]]] = None,
                 **kwargs: Any) -> None:
        self.pipeline = pipeline

        if isinstance(downstream_pipes, str):
            downstream_pipes = [downstream_pipes]
        self.downstream_pipes = downstream_pipes

    def __call__(self) -> Iterator[str]:
        while True:
            infile = (yield)
            infile = self.backup_infile(infile)
            if self.pipeline.verbosity >= 2:
                print(f"{self}: {infile}")
            outfile = self.get_outfile(infile)
            if outfile is None:
                continue
            if not isfile(outfile):
                self.process_file_in_pipeline(infile, outfile)
            self.log_outfile(outfile)
            if self.downstream_pipes is not None:
                for pipe in self.downstream_pipes:
                    self.pipeline.pipes[pipe].send(outfile)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.desc}>"

    def __str__(self) -> str:
        return self.__repr__()

    def backup_infile(self, infile: str) -> str:
        if self.pipeline.wip_directory not in infile:
            name = self.get_original_name(infile)
            ext = self.get_extension(infile)
            if not isdir(f"{self.pipeline.wip_directory}/{name}"):
                makedirs(f"{self.pipeline.wip_directory}/{name}")
            new_infile = f"{self.pipeline.wip_directory}/{name}/{name}.{ext}"
            copyfile(infile, new_infile)

            return new_infile
        else:
            return infile

    def get_extension(self, infile: str) -> str:
            return splitext(basename(infile))[1].strip(".")

    def get_original_name(self, infile: str) -> str:
        if self.pipeline.wip_directory in infile:
            return basename(dirname(infile))
        else:
            return splitext(basename(infile))[0]

    def get_outfile(self, infile: str) -> str:
        original_name = self.get_original_name(infile)
        desc_so_far = splitext(basename(infile))[0].replace(original_name, "")
        outfile = f"{desc_so_far}_{self.desc}.png".lstrip("_")
        outfile = f"{self.pipeline.wip_directory}/{original_name}/{outfile}"

        return outfile

    def log_outfile(self, outfile: str) -> None:
        name = self.get_original_name(outfile)
        if name not in self.pipeline.log:
            self.pipeline.log[name] = [basename(outfile)]
        else:
            self.pipeline.log[name].append(basename(outfile))

    def process_file_in_pipeline(self, infile: str, outfile: str) -> None:
        self.process_file(infile, outfile,
                          verbosity=self.pipeline.verbosity)

    @staticmethod
    def get_indented_text(text: str) -> str:
        columns = get_terminal_size((80, 20)).columns
        wrapper = TextWrapper(initial_indent="    ", width=columns - 4,
                              subsequent_indent="    ")
        return wrapper.fill(text)

    # region Class Methods

    @classmethod
    def construct_argparser(
            cls, description: Optional[str] = None) -> ArgumentParser:
        """
        Constructs argument parser

        Returns:
            parser (ArgumentParser): Argument parser
        """

        def infile_argument(value: str) -> str:
            if not isinstance(value, str):
                raise ArgumentError()

            value = expandvars(value)
            if not isfile(value):
                raise ArgumentError(f"infile '{value}' does not exist")
            elif not access(value, R_OK):
                raise ArgumentError(f"infile '{value}' cannot be read")

            return value

        def outfile_argument(value: str) -> str:
            if not isinstance(value, str):
                raise ArgumentError()

            value = expandvars(value)
            if isfile(value):
                if not access(value, W_OK):
                    raise ArgumentError(f"outfile '{value}' cannot be written")
            else:
                directory = dirname(value)
                if directory == "":
                    directory = getcwd()
                if not access(directory, W_OK):
                    raise ArgumentError(f"outfile '{value}' cannot be written")

            return value

        parser = ArgumentParser(
            description=description,
            formatter_class=RawDescriptionHelpFormatter)
        verbosity = parser.add_mutually_exclusive_group()
        verbosity.add_argument(
            "-v", "--verbose",
            action="count",
            default=1,
            dest="verbosity",
            help="enable verbose output, may be specified more than once")
        verbosity.add_argument(
            "-q", "--quiet",
            action="store_const",
            const=0,
            dest="verbosity",
            help="disable verbose output")
        parser.add_argument(
            "infile",
            type=infile_argument,
            help="input file")
        parser.add_argument(
            "outfile",
            type=outfile_argument,
            help="output file")

        return parser

    @classmethod
    def main(cls) -> None:
        """Parses and validates arguments, constructs and calls object"""

        parser = cls.construct_argparser()
        kwargs = vars(parser.parse_args())
        cls.process_file(**kwargs)

    @classmethod
    @abstractmethod
    def process_file(cls, infile: str, outfile: str, **kwargs: Any) -> None:
        pass

    # endregion
