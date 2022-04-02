#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Command line interface for utilities."""
from __future__ import annotations

from abc import ABC, abstractmethod
from inspect import cleandoc
from typing import Type

from pipescaler.common import CommandLineInterface


class UtilityCommandLineInterface(CommandLineInterface, ABC):
    """Command line interface for utilities."""

    @classmethod
    @property
    def description(cls) -> str:
        """Long description of this tool displayed below usage."""
        if cls.utility.__doc__:
            return cleandoc(cls.utility.__doc__)
        return ""

    @classmethod
    @property
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser."""
        return cls.__name__.removesuffix("CL").lower()

    @classmethod
    @property
    @abstractmethod
    def utility(cls) -> Type:
        """Type of utility wrapped by command line interface."""
        raise NotImplementedError()
