#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Minimal implementation of PipeObject for testing."""
from __future__ import annotations

from pipescaler.common import PathLike, validate_output_file
from pipescaler.core.pipelines import PipeObject


class TestPipeObject(PipeObject):
    """Minimal implementation of PipeObject for testing."""
    def save(self, path: PathLike) -> None:
        """Save object to file and set path.

        Arguments:
            path: Path to which to save object
        """
        path = validate_output_file(path)
        path.touch()
