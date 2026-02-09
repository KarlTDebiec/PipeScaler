#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for TopazVideoAiRunner."""

from __future__ import annotations

from pathlib import Path

from pipescaler.common.file import get_temp_directory_path
from pipescaler.video.runners import TopazVideoAiRunner


def test_repr_round_trip():
    """Test TopazVideoAiRunner repr round-trip recreation."""
    with get_temp_directory_path() as working_dir_path:
        runner = TopazVideoAiRunner(
            arguments="-i in.mp4 -o out.mp4",
            working_dir_path=str(working_dir_path),
            timeout=1,
        )
        recreated = eval(repr(runner))
        assert recreated.arguments == runner.arguments
        assert recreated.timeout == runner.timeout
        assert recreated.working_dir_path == Path(working_dir_path)
