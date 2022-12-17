#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for Utility command line interfaces."""
from __future__ import annotations

from abc import ABC, abstractmethod
from inspect import cleandoc
from typing import Any, Type

from pipescaler.common import CommandLineInterface
from pipescaler.core.utility import Utility


class UtilityCli(CommandLineInterface, ABC):
    """Abstract base class for Utility command line interfaces."""

    @classmethod
    def description(cls) -> str:
        """Long description of this tool displayed below usage."""
        if cls.utility.__doc__:
            return cleandoc(cls.utility.__doc__)
        return ""

    @classmethod
    def execute(cls, **kwargs: Any) -> None:
        """Execute with provided keyword arguments.

        TODO: Decide on a consistent way for ProcessorCli and UtilityCli to manage
          arguments destined for __init__ and arguments destined for __call__

        Arguments:
            **kwargs: Command-line arguments
        """
        verbosity = kwargs.pop("verbosity", 1)
        utility = cls.utility(verbosity=verbosity)  # noqa
        utility(**kwargs)

    @classmethod
    def main(cls) -> None:
        """Execute from command line."""
        parser = cls.argparser()
        kwargs = vars(parser.parse_args())
        cls.execute(**kwargs)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser."""
        return cls.__name__.removesuffix("Cli").lower()

    @classmethod
    @abstractmethod
    def utility(cls) -> Type[Utility]:
        """Type of utility wrapped by command line interface."""
        raise NotImplementedError()
