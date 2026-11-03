#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for direct in-memory image writing into atomic checkpoints."""

from __future__ import annotations

from os import utime
from pathlib import Path
from struct import unpack_from
from unittest.mock import Mock

import pytest
from PIL import Image

from pipescaler.image.core.pipelines import PipeImage
from pipescaler.image.pipelines import ImageCheckpointManager
from pipescaler.image.pipelines.termini import ImageDirectoryTerminus
from pipescaler.image.writers import DdsWriter


def test_stale_checkpoint_is_rewritten(tmp_path: Path):
    """Honor input mtimes when deciding whether to run the writer again.

    Arguments:
        tmp_path: input and checkpoint directory
    """
    input_path = tmp_path / "source.png"
    Image.new("RGB", (4, 4), "red").save(input_path)
    source = PipeImage(path=input_path)
    manager = ImageCheckpointManager(
        tmp_path / "checkpoints", validate_input_mtime=True
    )
    writer = Mock(wraps=DdsWriter())
    segment = manager.post_writer("texture.dds")(writer)
    checkpoint_path = segment(source)[0].path
    assert checkpoint_path is not None
    segment(source)
    assert writer.call_count == 1
    newer_ns = checkpoint_path.stat().st_mtime_ns + 2_000_000_000
    utime(input_path, ns=(newer_ns, newer_ns))

    segment(source)

    assert writer.call_count == 2


@pytest.mark.parametrize("file_backed", [False, True])
def test_dds_checkpoint_and_terminus(tmp_path: Path, file_backed: bool):
    """Retain DDS mip bytes, input identity, and lineage through final output.

    Arguments:
        tmp_path: directory for input, checkpoint, and final files
        file_backed: whether the source has a filesystem path
    """
    manager = ImageCheckpointManager(tmp_path / "checkpoints")
    writer = Mock(wraps=DdsWriter())
    segment = manager.post_writer("99_dds.dds")(writer)
    pixels = Image.new("RGBA", (8, 8), (32, 64, 96, 128))
    if file_backed:
        input_path = tmp_path / "source.one.png"
        pixels.save(input_path)
        source = PipeImage(path=input_path, location_path=Path("nested"))
    else:
        source = PipeImage(
            image=pixels, name="source.one", location_path=Path("nested")
        )
    source_path = source.path

    output = segment(source)[0]
    cached = segment(source)[0]
    terminus = ImageDirectoryTerminus(tmp_path / "output")
    terminus(output)

    checkpoint_path = manager.dir_path / "nested" / "source.one" / "99_dds.dds"
    data = checkpoint_path.read_bytes()
    writer.assert_called_once()
    assert writer.call_args.args[0] is source.image
    assert output.path == cached.path == checkpoint_path
    assert output.name == source.name
    assert output.location == source.location
    assert output.parents == cached.parents == [source]
    assert source.path == source_path
    assert (source.location_name, "99_dds.dds") in manager.observed_checkpoints
    assert manager.get_cpts_of_segments(segment) == ["99_dds.dds"]
    assert unpack_from("<I", data, 28)[0] == 4
    assert (terminus.dir_path / "nested" / "source.one.dds").read_bytes() == data


@pytest.mark.parametrize("failure", ["exception", "malformed", "missing"])
@pytest.mark.parametrize("existing", [False, True])
def test_failed_write_preserves_checkpoint(
    tmp_path: Path, failure: str, existing: bool
):
    """Discard failed writes without publishing or replacing a prior checkpoint.

    Arguments:
        tmp_path: checkpoint directory
        failure: writer failure behavior to exercise
        existing: whether a valid checkpoint already exists
    """
    manager = ImageCheckpointManager(
        tmp_path / "checkpoints", validate_input_mtime=True
    )
    source = PipeImage(image=Image.new("RGBA", (4, 4)), name="source")
    checkpoint_path = manager.dir_path / "source" / "texture.dds"
    if existing:
        DdsWriter()(Image.new("RGB", (4, 4), "blue"), checkpoint_path)
    original = checkpoint_path.read_bytes() if existing else None

    def fail_write(image: Image.Image, output_path: Path):
        """Produce partial output, no output, or an exception.

        Arguments:
            image: unused source pixels
            output_path: temporary checkpoint destination
        Raises:
            OSError: when the selected failure is an exception
        """
        if failure != "missing":
            output_path.write_bytes(b"partial")
        if failure == "exception":
            raise OSError("writer failed")

    segment = manager.post_writer("texture.dds")(fail_write)
    with pytest.raises(OSError):
        segment(source)
    assert manager.observed_checkpoints == set()
    if existing:
        assert checkpoint_path.read_bytes() == original
        assert list(checkpoint_path.parent.iterdir()) == [checkpoint_path]
    else:
        assert not checkpoint_path.exists()
        assert list(checkpoint_path.parent.iterdir()) == []


@pytest.mark.parametrize("count", [0, 2])
def test_requires_one_input(tmp_path: Path, count: int):
    """Reject unsupported input cardinality before accessing images or files.

    Arguments:
        tmp_path: checkpoint directory
        count: number of source images to pass
    """
    manager = ImageCheckpointManager(tmp_path)
    segment = manager.post_writer("texture.dds")(DdsWriter())
    source = PipeImage(image=Image.new("RGB", (4, 4)), name="source")
    with pytest.raises(ValueError, match="requires 1 input"):
        segment(*([source] * count))
