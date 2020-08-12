#!/usr/bin/env python
#   common/cltool.py
#
#   Copyright (C) 2017-2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
""""""
################################### MODULES ###################################
from abc import ABC
from argparse import (ArgumentParser,
                      ArgumentTypeError, FileType, RawDescriptionHelpFormatter,
                      _SubParsersAction)
from inspect import currentframe, getframeinfo
from os import R_OK, W_OK, access, getcwd
from os.path import basename, dirname, exists, expandvars, isdir, isfile, join
from typing import Any, Callable, Dict, Optional, Union

# noinspection Mypy
from . import package_root


################################### CLASSES ###################################
class CLTool(ABC):
    """Abstract base class for command line tools"""

    # region Builtins

    def __init__(self, **kwargs: Any) -> None:
        pass

    def __call__(self, **kwargs: Any) -> None:
        raise NotImplementedError()

    # endregion

    # region Properties

    @property
    def embed_kw(self) -> Dict[str, str]:
        """Use ``IPython.embed(**self.embed_kw)`` for better prompt"""
        frame = currentframe()
        if frame is None:
            raise ValueError()
        frameinfo = getframeinfo(frame.f_back)
        file = frameinfo.filename.replace(package_root, "")
        func = frameinfo.function
        number = frameinfo.lineno - 1
        header = ""

        if self.verbosity >= 1:
            header = f"IPython prompt in file {file}, function {func}," \
                     f" line {number}\n"
        if self.verbosity >= 2:
            header += "\n"
            with open(frameinfo.filename, "r") as infile:
                lines = [(i, line) for i, line in enumerate(infile)
                         if i in range(number - 5, number + 6)]
            for i, line in lines:
                header += f"{i:5d} {'>' if i == number else ' '} " \
                          f"{line.rstrip()}\n"

        return {"header": header}

    @property
    def verbosity(self) -> int:
        """int: Level of output to provide"""
        if not hasattr(self, "_verbosity"):
            self._verbosity = 1
        return self._verbosity

    @verbosity.setter
    def verbosity(self, value: int) -> None:
        if not isinstance(value, int) and value >= 0:
            raise ValueError(self._generate_setter_exception(value))
        self._verbosity = value

    # endregion

    # region Class Methods

    @classmethod
    def construct_argparser(
            cls,
            description: Optional[str] = None,
            parser: Optional[Union[ArgumentParser, _SubParsersAction]] = None,
            **kwargs: Any) -> ArgumentParser:
        """
        Constructs argument parser

        Args:
            description (Optional[str]):
            parser (Optional[Union[ArgumentParser, _SubParsersAction]]):
              Nascent argument parser
            kwargs (Any): Additional keyword arguments

        Returns:
            ArgumentParser: Argument parser
        """
        if isinstance(parser, ArgumentParser):
            parser = parser
        elif isinstance(parser, _SubParsersAction):
            parser = parser.add_parser(
                name=cls.__name__.lower(),
                description=description,
                help=description,
                formatter_class=RawDescriptionHelpFormatter)
        elif parser is None:
            # noinspection PyTypeChecker
            parser = ArgumentParser(
                description=description,
                formatter_class=RawDescriptionHelpFormatter)

        # General
        verbosity = parser.add_mutually_exclusive_group()
        verbosity.add_argument(
            "-v", "--verbose",
            action="count",
            default=1,
            dest="verbosity",
            help="enable verbose output, may be specified "
                 "more than once")
        verbosity.add_argument(
            "-q", "--quiet",
            action="store_const",
            const=0,
            dest="verbosity",
            help="disable verbose output")

        return parser

    @classmethod
    def main(cls) -> None:
        """Parses and validates arguments, constructs and calls object"""
        parser = cls.construct_argparser()
        kwargs = vars(parser.parse_args())
        cls(**kwargs)()

    # endregion

    # region Static methods

    @staticmethod
    def float_argument(
            min_value: Optional[float] = None,
            max_value: Optional[float] = None) \
            -> Union[Callable[[str], float], FileType]:
        def func(value: str) -> float:
            try:
                # noinspection Mypy
                value = float(value)
            except ValueError:
                raise ArgumentTypeError(
                    f"input value '{value}' is of type '{type(value)}', not "
                    f"float")
            if min_value is not None and value < min_value:
                raise ArgumentTypeError(
                    f"input value '{value}' is less than minimum value of "
                    f"'{min_value}'")
            if max_value is not None and value > max_value:
                raise ArgumentTypeError(
                    f"input value '{value}' is greater than maximum value of "
                    f"'{max_value}'")
            return value

        return func

    @staticmethod
    def indir_argument() -> Callable[[str], str]:
        def func(value: str) -> str:
            if not isinstance(value, str):
                raise ArgumentTypeError(
                    f"input directory '{value}' is of type '{type(value)}', "
                    f"not str")

            value = expandvars(value)
            if exists(value):
                if isdir(value):
                    if not access(value, R_OK):
                        raise ArgumentTypeError(
                            f"input directory '{value}' exists but cannot be "
                            f"read")
                else:
                    raise ArgumentTypeError(
                        f"input directory '{value}' exists but is not a "
                        f"directory")
            else:
                raise ArgumentTypeError(
                    f"input directory '{value}' does not exist")

            return value

        return func

    @staticmethod
    def indir_or_infile_argument() -> Callable[[str], str]:
        def func(value: str) -> str:
            if not isinstance(value, str):
                raise ArgumentTypeError(
                    f"input file/directory '{value}' is of type "
                    f"'{type(value)}', not str")

            value = expandvars(value)
            directory = dirname(value)
            if directory == "":
                directory = getcwd()
            value = join(directory, basename(value))
            if exists(value):
                if isfile(value):
                    if not access(value, R_OK):
                        raise ArgumentTypeError(
                            f"input file '{value}' exists but cannot be read")
                else:
                    raise ArgumentTypeError(
                        f"input file '{value}' exists but is not a file")
            else:
                raise ArgumentTypeError(f"input file '{value}' does not exist")

            return value

        return func

    @staticmethod
    def infile_argument() -> Callable[[str], str]:
        def func(value: str) -> str:
            if not isinstance(value, str):
                raise ArgumentTypeError(
                    f"input file '{value}' is of type '{type(value)}', not "
                    f"str")

            value = expandvars(value)
            directory = dirname(value)
            if directory == "":
                directory = getcwd()
            value = join(directory, basename(value))
            if exists(value):
                if isfile(value):
                    if not access(value, R_OK):
                        raise ArgumentTypeError(
                            f"input file '{value}' exists but cannot be read")
                else:
                    raise ArgumentTypeError(
                        f"input file '{value}' exists but is not a file")
            else:
                raise ArgumentTypeError(f"input file '{value}' does not exist")

            return value

        return func

    @staticmethod
    def outdir_argument() -> Callable[[str], str]:
        def func(value: str) -> str:
            if not isinstance(value, str):
                raise ArgumentTypeError(
                    f"output directory '{value}' is of type '{type(value)}', "
                    f"not str")

            value = expandvars(value)
            if exists(value):
                if isdir(value):
                    if not access(value, W_OK):
                        raise ArgumentTypeError(
                            f"output directory '{value}' exists but cannot be "
                            f"written")
                else:
                    raise ArgumentTypeError(
                        f"output directory '{value}' exists but is not a "
                        f"directory")
            else:
                raise ArgumentTypeError(
                    f"output directory '{value}' does not exist")

            return value

        return func

    @staticmethod
    def outfile_argument() -> Callable[[str], str]:
        def func(value: str) -> str:
            if not isinstance(value, str):
                raise ArgumentTypeError(
                    f"output file '{value}' is of type '{type(value)}', not "
                    f"str")

            value = expandvars(value)
            directory = dirname(value)
            if directory == "":
                directory = getcwd()
            value = join(directory, basename(value))
            if exists(value):
                if isfile(value):
                    if not access(value, W_OK):
                        raise ArgumentTypeError(
                            f"output file '{value}' exists but cannot be "
                            f"written")
                else:
                    raise ArgumentTypeError(
                        f"output file '{value}' exists but is not a file")
            else:
                if exists(directory):
                    if isdir(directory):
                        if not access(directory, W_OK):
                            raise ArgumentTypeError(
                                f"output directory '{directory}' exists but "
                                f"cannot be written")
                    else:
                        raise ArgumentTypeError(
                            f"output directory '{directory}' exists but is "
                            f"not a directory")
                else:
                    raise ArgumentTypeError(
                        f"output directory '{directory}' does not exist")

            return value

        return func

    # endregion

    # region Private methods

    def _generate_setter_exception(self, value: Any) -> str:
        """
        Generates Exception text for setters that are passed invalid values

        Args:
            value (Any): Provided value

        Returns:
            str: Exception text
        """
        frame = currentframe()
        if frame is None:
            raise ValueError()
        frameinfo = getframeinfo(frame.f_back)
        return f"Property '{type(self).__name__}.{frameinfo.function}' " \
               f"was passed invalid value '{value}' " \
               f"of type '{type(value).__name__}'. " \
               f"Expects '{getattr(type(self), frameinfo.function).__doc__}'."

    # endregion
