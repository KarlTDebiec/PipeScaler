#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for Utility command-line interfaces."""
from __future__ import annotations

from abc import ABC, abstractmethod
from inspect import cleandoc
from typing import Any, Type

from pipescaler.common import CommandLineInterface
from pipescaler.core.utility import Utility


class UtilityCli(CommandLineInterface, ABC):
    """Abstract base class for Utility command-line interfaces."""

    @classmethod
    def description(cls) -> str:
        """Long description of this tool displayed below usage."""
        return cleandoc(str(cls.utility().__doc__)) if cls.utility().__doc__ else ""

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser."""
        return cls.__name__.removesuffix("Cli").lower()

    @classmethod
    def _main(cls, **kwargs: Any) -> None:
        """Execute with provided keyword arguments.

        May be overridden to distribute keyword arguments between initialization of the
        utility and the call to its run method.

        Arguments:
            **kwargs: Keyword arguments
        """
        utility_cls = cls.utility()
        utility_cls.run(**kwargs)

    @classmethod
    @abstractmethod
    def utility(cls) -> Type[Utility]:
        """Type of utility wrapped by command-line interface."""
        raise NotImplementedError()
