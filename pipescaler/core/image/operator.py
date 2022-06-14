#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for image operators."""
from __future__ import annotations

from abc import ABC
from inspect import cleandoc
from typing import Any


class Operator(ABC):
    """Abstract base class for image operators."""

    def __init__(self, **kwargs: Any) -> None:
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    @classmethod
    @property
    def help_markdown(cls) -> str:
        """Short description of this image operator in markdown, with links."""
        if cls.__doc__:
            return cleandoc(cls.__doc__).split(". ", maxsplit=1)[0]
        return ""

    @classmethod
    @property
    def inputs(cls) -> dict[str, tuple[str, ...]]:
        raise NotImplementedError()

    @classmethod
    @property
    def outputs(cls) -> dict[str, tuple[str, ...]]:
        raise NotImplementedError()
