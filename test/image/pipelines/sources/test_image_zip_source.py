#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for images extracted from ZIP archives."""

from __future__ import annotations

import re
import tempfile
from io import BytesIO
from os import utime
from pathlib import Path
from zipfile import BadZipFile, ZipFile

import pytest
from PIL import Image

from pipescaler.image.operators.processors.mode_processor import ModeProcessor
from pipescaler.image.pipelines.segments import ImageProcessorSegment
from pipescaler.image.pipelines.sources import ImageZipSource
from pipescaler.pipelines.checkpoint_manager import CheckpointManager


def test_borrowed_image_outlives_wrapper(input_path: Path):
    """Remove extracted files while a borrowed image outlives its temporary wrapper.

    Arguments:
        input_path: archive containing nested images
    """
    with ImageZipSource(input_path, inclusions={r".*\.png$"}) as source:
        borrowed = next(source).image
        assert borrowed.size == (2, 3)
        paths = list(source.file_paths)
    assert all(not path.exists() for path in paths)
    assert borrowed.getpixel((0, 0)) == (255, 0, 0)


def test_checkpoint_freshness(input_path: Path, tmp_path: Path):
    """Reuse checkpoints across extractions and invalidate them after archive edits.

    Arguments:
        input_path: archive containing nested images
        tmp_path: temporary test directory
    """
    archive_mtime_ns = 1_700_000_000_000_000_000
    utime(input_path, ns=(archive_mtime_ns, archive_mtime_ns))
    checkpoint_path = tmp_path / "checkpoint.png"
    checkpoint_path.touch()
    checkpoint_mtime_ns = archive_mtime_ns + 1_000_000_000
    utime(checkpoint_path, ns=(checkpoint_mtime_ns, checkpoint_mtime_ns))
    manager = CheckpointManager(tmp_path / "checkpoints", validate_input_mtime=True)
    for _ in range(2):
        with ImageZipSource(input_path, inclusions={r".*\.png$"}) as source:
            image = next(source)
            assert image.path is not None
            assert image.path.stat().st_mtime_ns == archive_mtime_ns
            assert manager.checkpoints_current((image,), (checkpoint_path,))
    updated_mtime_ns = checkpoint_mtime_ns + 1_000_000_000
    utime(input_path, ns=(updated_mtime_ns, updated_mtime_ns))
    with ImageZipSource(input_path, inclusions={r".*\.png$"}) as source:
        assert not manager.checkpoints_current((next(source),), (checkpoint_path,))


def test_corrupt_member_cleanup(
    input_path: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Remove partially extracted files when a member fails its CRC check.

    Arguments:
        input_path: archive containing stored PNGs
        tmp_path: temporary archive and extraction directory
        monkeypatch: temporary directory configuration replacement
    """
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
    with ZipFile(input_path) as archive:
        payload = archive.read("nested/image.two.png")
    data = bytearray(input_path.read_bytes())
    offset = data.index(payload)
    data[offset] ^= 1
    input_path.write_bytes(data)
    with pytest.raises(BadZipFile, match="CRC"):
        ImageZipSource(input_path)
    assert list(tmp_path.iterdir()) == [input_path]


def test_early_context_exit(input_path: Path):
    """Remove every selected file even when processing stops early.

    Arguments:
        input_path: archive containing nested images
    Raises:
        RuntimeError: if simulated processing fails
    """
    with pytest.raises(RuntimeError, match="processing failed"):
        with ImageZipSource(input_path) as source:
            next(source)
            paths = list(source.file_paths)
            raise RuntimeError("processing failed")
    assert all(not path.exists() for path in paths)


def test_filters_and_reverse_sort(input_path: Path):
    """Apply compiled filters to forward-slash names and honor custom sorting.

    Arguments:
        input_path: archive containing nested images
    """
    with ImageZipSource(
        input_path,
        inclusions={re.compile(r"nested/.*\.png$")},
        exclusions={r".*one\.png$"},
        sort=len,
        reverse=True,
    ) as source:
        assert [image.name for image in source] == ["image.two"]
    with ImageZipSource(input_path, sort=len, reverse=True) as source:
        assert [image.name for image in source] == [
            "image.two",
            "image.one",
            "notes",
            "root",
        ]


def test_invalid_and_empty_archives(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Reject invalid ZIP data without leaking files and accept empty archives.

    Arguments:
        tmp_path: temporary archive and extraction directory
        monkeypatch: temporary directory configuration replacement
    """
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
    input_path = tmp_path / "input.zip"
    input_path.write_bytes(b"invalid ZIP")
    with pytest.raises(BadZipFile):
        ImageZipSource(input_path)
    assert list(tmp_path.iterdir()) == [input_path]
    with ZipFile(input_path, "w"):
        pass
    with ImageZipSource(input_path) as source:
        assert list(source) == []


def test_modified_image_outlives_source(input_path: Path):
    """Retain replacement pixels after the source releases its temporary files.

    Arguments:
        input_path: archive containing nested images
    """
    with ImageZipSource(input_path, inclusions={r".*\.png$"}) as source:
        image = next(source)
        image.image = image.image.resize((4, 6))
    assert image.path is None
    assert image.image.size == (4, 6)
    assert image.image.getpixel((0, 0)) == (255, 0, 0)


def test_no_op_processor_output_outlives_source(input_path: Path):
    """Retain shared pixels in a no-op processor output after source cleanup.

    Arguments:
        input_path: archive containing nested images
    """
    with ImageZipSource(input_path, inclusions={r".*\.png$"}) as source:
        image = next(source)
        (output,) = ImageProcessorSegment(ModeProcessor("RGB"))(image)
        assert output.path is None
        assert output.image is image.image
        assert output.parents == [image]
        paths = list(source.file_paths)
    assert all(not path.exists() for path in paths)
    assert output.image.getpixel((0, 0)) == (255, 0, 0)


def test_normalized_member_filters(tmp_path: Path):
    """Apply filters and preserve locations after normalizing member separators.

    Arguments:
        tmp_path: temporary archive directory
    """
    input_path = tmp_path / "input.zip"
    with ZipFile(input_path, "w") as archive:
        archive.writestr("./nested//image.png", b"undecoded bytes")
    with ImageZipSource(input_path, inclusions={r"nested/.*\.png$"}) as source:
        image = next(source)
        assert image.name == "image"
        assert image.location == Path("nested")
        assert image.path is not None
        assert image.path.read_bytes() == b"undecoded bytes"


def test_same_image_assignment_outlives_source(input_path: Path):
    """Release file handles when a no-op assignment retains the same pixel object.

    Arguments:
        input_path: archive containing nested images
    """
    with ImageZipSource(input_path, inclusions={r".*\.png$"}) as source:
        image = next(source)
        original_pixels = image.image
        image.image = ModeProcessor("RGB")(image.image)
        assert image.path is None
        assert image.image is original_pixels
        paths = list(source.file_paths)
    assert all(not path.exists() for path in paths)
    assert image.image.getpixel((0, 0)) == (255, 0, 0)


def test_sorted_images_and_lifetime(input_path: Path):
    """Keep extracted paths and lazy images usable after iterator exhaustion.

    Arguments:
        input_path: archive containing nested images
    """
    with ImageZipSource(input_path, inclusions={r".*\.png$"}) as source:
        images = list(source)
        assert [image.location_name for image in images] == [
            str(Path("nested/image.one")),
            str(Path("nested/image.two")),
            "root",
        ]
        assert all(image.parents is None for image in images)
        assert all(image.path is not None and image.path.is_file() for image in images)
        assert images[0].image.size == (2, 3)
        assert images[1].image.getpixel((0, 0)) == (255, 0, 0)
        paths = list(source.file_paths)
        with pytest.raises(StopIteration):
            next(source)
    assert all(not path.exists() for path in paths)
    source.close()
    with pytest.raises(StopIteration):
        next(source)
    with pytest.raises(ValueError, match="closed ZIP source"):
        with source:
            pass


@pytest.fixture
def input_path(tmp_path: Path) -> Path:
    """Provide an archive with nested PNGs, metadata, and a non-image file.

    Arguments:
        tmp_path: temporary test directory
    """
    input_path = tmp_path / "input.zip"
    buffer = BytesIO()
    Image.new("RGB", (2, 3), "red").save(buffer, format="PNG")
    with ZipFile(input_path, "w") as archive:
        archive.writestr("nested/image.two.png", buffer.getvalue())
        archive.writestr("nested/image.one.png", buffer.getvalue())
        archive.writestr("root.png", buffer.getvalue())
        archive.writestr("nested/", b"")
        archive.writestr("nested/.DS_Store", b"metadata")
        archive.writestr("notes.txt", b"notes")
    return input_path


@pytest.mark.parametrize(
    "member_names", [["../escape.png"], ["a.png", "A.PNG"], ["a", "a/b.png"]]
)
def test_rejects_unsafe_members(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, member_names: list[str]
):
    """Clean up partial extraction when selected member paths are invalid.

    Arguments:
        tmp_path: temporary archive and extraction directory
        monkeypatch: temporary directory configuration replacement
        member_names: unsafe or colliding member names
    """
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
    input_path = tmp_path / "input.zip"
    with ZipFile(input_path, "w") as archive:
        for member_name in member_names:
            archive.writestr(member_name, b"file")
    with pytest.raises(ValueError, match="ZIP member path"):
        ImageZipSource(input_path)
    assert list(tmp_path.iterdir()) == [input_path]
