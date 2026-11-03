#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for unsupported video saving."""

from __future__ import annotations

from pathlib import Path

import pytest

from pipescaler.video.core.pipelines import PipeVideo


@pytest.mark.parametrize("existing_output", [False, True])
def test_save_preserves_state_and_files(tmp_path: Path, existing_output: bool):
    """Reject saving without changing the source, target, or object path.

    Arguments:
        tmp_path: temporary test directory
        existing_output: whether the output file already exists
    """
    input_path = tmp_path / "input.mp4"
    input_path.write_bytes(b"source video")
    output_path = tmp_path / "new" / "output.mp4"
    if existing_output:
        output_path.parent.mkdir()
        output_path.write_bytes(b"existing output")
    video = PipeVideo(path=input_path)

    with pytest.raises(NotImplementedError, match="video encoding"):
        video.save(output_path)

    assert video.path == input_path
    assert input_path.read_bytes() == b"source video"
    assert video._video is None
    if existing_output:
        assert output_path.read_bytes() == b"existing output"
    else:
        assert not output_path.parent.exists()
