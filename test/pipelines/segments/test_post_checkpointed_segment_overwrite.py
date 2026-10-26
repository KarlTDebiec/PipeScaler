#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for replacing stale image post-checkpoints."""

from __future__ import annotations

from os import utime
from pathlib import Path
from unittest.mock import Mock

from PIL import Image

from pipescaler.core.pipelines import PipeObject
from pipescaler.image.core.pipelines import PipeImage
from pipescaler.pipelines import CheckpointManager


def test_stale_image_checkpoint_is_overwritten(tmp_path: Path):
    """Recompute a stale post-checkpoint and replace the saved image pixels.

    Arguments:
        tmp_path: temporary directory for input and checkpoint files
    """
    input_path = tmp_path / "source.png"
    Image.new("RGB", (2, 2), "red").save(input_path)
    cp_manager = CheckpointManager(tmp_path / "checkpoints", validate_input_mtime=True)

    def copy_image(input_obj: PipeObject) -> tuple[PipeObject, ...]:
        """Return a copy of the input image with its lineage retained.

        Arguments:
            input_obj: image whose pixels are copied
        Returns:
            copied image within a tuple
        """
        assert isinstance(input_obj, PipeImage)
        return (PipeImage(image=input_obj.image.copy(), parents=input_obj),)

    segment = Mock(wraps=copy_image)
    wrapper = cp_manager.post_segment("output.png")(segment)
    wrapper(PipeImage(path=input_path))
    checkpoint_path = cp_manager.dir_path / "source" / "output.png"
    Image.new("RGB", (2, 2), "blue").save(input_path)
    newer_mtime_ns = checkpoint_path.stat().st_mtime_ns + 1_000_000_000
    utime(input_path, ns=(newer_mtime_ns, newer_mtime_ns))

    outputs = wrapper(PipeImage(path=input_path))

    assert segment.call_count == 2
    assert outputs[0].path == checkpoint_path
    with Image.open(checkpoint_path) as image:
        assert image.getpixel((0, 0)) == (0, 0, 255)
