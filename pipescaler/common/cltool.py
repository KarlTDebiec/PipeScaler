#!/usr/bin/env python
#   common/cltool.py
#
#   Copyright (C) 2017-2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""
General-purpose command-line tool base class not tied to a particular project.
Last updated 2020-08-15
"""
################################### MODULES ###################################
from abc import ABC
from argparse import (ArgumentParser,
                      ArgumentTypeError, RawDescriptionHelpFormatter,
                      _SubParsersAction)
from inspect import currentframe, getframeinfo
from typing import Any, Callable, Optional, Union

# noinspection Mypy
from .general import validate_input_path, validate_output_path


################################### CLASSES ###################################
class CLTool(ABC):
    """Abstract base class for command line tools"""

    # region Builtins

    def __init__(self, **kwargs: Any) -> None:
        """Initialize, including cross-argument validation and value storage"""
        pass

    def __call__(self, **kwargs: Any) -> Any:
        """Perform operations"""
        raise NotImplementedError()

    # endregion

    # region Properties

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
            description (Optional[str]): Description of parser
            parser (Optional[Union[ArgumentParser, _SubParsersAction]]):
              Nascent argument parser or subparsers
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
            max_value: Optional[float] = None) -> Callable[[str], float]:
        """TODO: Document"""

        def func(value: Union[str, float]) -> float:
            try:
                value = float(value)
            except ValueError:
                raise ArgumentTypeError(
                    f"'{value}' is of type '{type(value)}', not float")

            if min_value is not None and value < min_value:
                raise ArgumentTypeError(f"'{value}' is less than minimum "
                                        f"value of '{min_value}'")
            if max_value is not None and value > max_value:
                raise ArgumentTypeError(f"'{value}' is greater than maximum "
                                        f"value of '{max_value}'")
            return value

        return func

    @staticmethod
    def input_path_argument(
            file_ok: bool = True,
            directory_ok: bool = False) -> Callable[[str], str]:
        """TODO: Document"""

        def func(value: str) -> str:
            # Try cast here, to raise ArgumentTypeError instead of ValueError
            try:
                value = str(value)
            except ValueError:
                raise ArgumentTypeError(
                    f"'{value}' is of type '{type(value)}', not str")
            return validate_input_path(value, file_ok, directory_ok)

        return func

    @staticmethod
    def output_path_argument(
            file_ok: bool = True,
            directory_ok: bool = False) -> Callable[[str], str]:
        """TODO: Document"""

        def func(value: str) -> str:
            # Try cast here, to raise ArgumentTypeError instead of ValueError
            try:
                value = str(value)
            except ValueError:
                raise ArgumentTypeError(
                    f"'{value}' is of type '{type(value)}', not str")
            return validate_output_path(value, file_ok, directory_ok)

        return func

    # endregion

    # region Private methods

    def _generate_setter_exception(self, value: Any) -> str:
        """
        Generates Exception text for setters that are passed invalid values

        TODO: Decide if this actually makes sense

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
