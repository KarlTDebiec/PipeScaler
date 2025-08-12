#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Processes image using Pytorch models loaded through Spandrel."""

from __future__ import annotations

from typing import Any


class SpandrelProcessor:
    """Processes image using Pytorch models loaded through Spandrel."""

    def __init__(self, **kwargs: Any):
        """Initialize.

        Arguments:
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

    @classmethod
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links."""
        return (
            "Processes image using Pytorch models loaded through "
            "[Spandrel](https://github.com/chaiNNer-org/spandrel)."
        )
