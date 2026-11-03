#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for transactional ZIP image output."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import pytest
from PIL import Image

from pipescaler.image.core.pipelines import PipeImage
from pipescaler.image.pipelines.sources import ImageZipSource
from pipescaler.image.pipelines.termini import ImageZipTerminus


def test_caught_write_failure_cannot_publish(tmp_path: Path):
    """Reject publication even when a duplicate-member error is caught by callers.

    Arguments:
        tmp_path: temporary output directory
    """
    output_path = tmp_path / "output.zip"
    output_path.write_bytes(b"existing output")
    image = PipeImage(image=Image.new("RGB", (1, 1)), name="same")
    with pytest.raises(ValueError, match="Cannot publish ZIP"):
        with ImageZipTerminus(output_path) as terminus:
            terminus(image)
            with pytest.raises(ValueError, match="Conflicting ZIP member"):
                terminus(image)
            with pytest.raises(ValueError, match="failed ZIP terminus"):
                terminus(image)
    assert output_path.read_bytes() == b"existing output"
    assert list(tmp_path.iterdir()) == [output_path]


def test_close_failure_preserves_destination(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Preserve output and remove temporary files if archive finalization fails.

    Arguments:
        tmp_path: temporary output directory
        monkeypatch: archive close replacement
    """
    original_close = ZipFile.close
    failed = False

    def fail_close(archive: ZipFile):
        """Fail the first writer close and allow subsequent cleanup.

        Arguments:
            archive: archive to close
        Raises:
            OSError: if this is the first writer close
        """
        nonlocal failed
        if archive.mode == "w" and not failed:
            failed = True
            raise OSError("finalization failed")
        original_close(archive)

    monkeypatch.setattr(ZipFile, "close", fail_close)
    output_path = tmp_path / "output.zip"
    output_path.write_bytes(b"existing output")
    with pytest.raises(OSError, match="finalization failed"):
        with ImageZipTerminus(output_path) as terminus:
            terminus(PipeImage(image=Image.new("RGB", (1, 1)), name="image"))
    assert output_path.read_bytes() == b"existing output"
    assert list(tmp_path.iterdir()) == [output_path]


def test_complete_collection_and_image_encodings(tmp_path: Path):
    """Publish nested PNGs and exact source bytes while removing old members.

    Arguments:
        tmp_path: temporary input and output directory
    """
    input_path = tmp_path / "image.one.jpg"
    Image.new("RGB", (2, 3), "red").save(input_path)
    output_path = tmp_path / "output.zip"
    with ZipFile(output_path, "w") as archive:
        archive.writestr("stale.txt", b"old")
    old_bytes = output_path.read_bytes()
    file_image = PipeImage(path=input_path, location_path=Path("nested"))
    memory_image = PipeImage(
        image=Image.new("RGBA", (3, 2), (1, 2, 3, 4)),
        name="image.two",
        location_path=Path("nested"),
    )
    with ImageZipTerminus(output_path) as terminus:
        terminus(file_image)
        terminus(memory_image)
        assert output_path.read_bytes() == old_bytes
    assert list(tmp_path.glob("*.zip")) == [output_path]
    with ZipFile(output_path) as archive:
        assert archive.namelist() == ["nested/image.one.jpg", "nested/image.two.png"]
        assert archive.read("nested/image.one.jpg") == input_path.read_bytes()
        with Image.open(BytesIO(archive.read("nested/image.two.png"))) as image:
            assert image.size == (3, 2)
            assert image.getpixel((0, 0)) == (1, 2, 3, 4)
    assert file_image.path == input_path
    assert memory_image.path is None


def test_context_lifecycle_and_empty_output(tmp_path: Path):
    """Require an active context and create a valid empty archive on success.

    Arguments:
        tmp_path: temporary output directory
    """
    output_path = tmp_path / "output.zip"
    terminus = ImageZipTerminus(output_path)
    image = PipeImage(image=Image.new("RGB", (1, 1)), name="image")
    with pytest.raises(ValueError, match="active context"):
        terminus(image)
    with terminus:
        with pytest.raises(ValueError, match="Cannot reenter"):
            with terminus:
                pass
    with ZipFile(output_path) as archive:
        assert archive.namelist() == []
    with pytest.raises(ValueError, match="active context"):
        terminus(image)
    with pytest.raises(ValueError, match="Cannot reenter"):
        with terminus:
            pass


def test_replace_failure_preserves_destination(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Preserve output and remove the completed temporary ZIP if replacement fails.

    Arguments:
        tmp_path: temporary output directory
        monkeypatch: path replacement override
    """

    def fail_replace(path: Path, target: Path):
        """Reject a simulated filesystem replacement.

        Arguments:
            path: temporary archive path
            target: destination archive path
        Raises:
            OSError: always, to simulate a filesystem failure
        """
        raise OSError("replacement failed")

    monkeypatch.setattr(Path, "replace", fail_replace)
    output_path = tmp_path / "output.zip"
    output_path.write_bytes(b"existing output")
    with pytest.raises(OSError, match="replacement failed"):
        with ImageZipTerminus(output_path):
            pass
    assert output_path.read_bytes() == b"existing output"
    assert list(tmp_path.iterdir()) == [output_path]


def test_zip_processing_round_trip(tmp_path: Path):
    """Process extracted images and reload the published ZIP with names intact.

    Arguments:
        tmp_path: temporary input and output directory
    """
    input_path = tmp_path / "input.zip"
    output_path = tmp_path / "nested" / "output.zip"
    with ImageZipTerminus(input_path) as terminus:
        terminus(PipeImage(image=Image.new("RGB", (2, 3), "red"), name="image.one"))
    with (
        ImageZipSource(input_path) as source,
        ImageZipTerminus(output_path) as terminus,
    ):
        for image in source:
            image.image = image.image.resize((4, 6))
            terminus(image)
    with ImageZipSource(output_path) as source:
        images = list(source)
        assert [image.name for image in images] == ["image.one"]
        assert images[0].image.size == (4, 6)
        assert images[0].image.getpixel((0, 0)) == (255, 0, 0)


@pytest.mark.parametrize("existing", [False, True])
def test_processing_failure_preserves_destination(tmp_path: Path, existing: bool):
    """Discard partial output after caller failures, preserving the destination.

    Arguments:
        tmp_path: temporary output directory
        existing: whether a destination already exists
    Raises:
        RuntimeError: if simulated processing fails
    """
    output_path = tmp_path / "output.zip"
    if existing:
        output_path.write_bytes(b"existing output")
    with pytest.raises(RuntimeError, match="processing failed"):
        with ImageZipTerminus(output_path) as terminus:
            terminus(PipeImage(image=Image.new("RGB", (1, 1)), name="first"))
            raise RuntimeError("processing failed")
    assert output_path.exists() == existing
    if existing:
        assert output_path.read_bytes() == b"existing output"
    assert list(tmp_path.iterdir()) == ([output_path] if existing else [])


@pytest.mark.parametrize("location_path", [Path("../escape"), Path("/absolute")])
def test_unsafe_output_location(tmp_path: Path, location_path: Path):
    """Reject output paths that escape the archive's relative namespace.

    Arguments:
        tmp_path: temporary output directory
        location_path: unsafe image location
    """
    output_path = tmp_path / "output.zip"
    image = PipeImage(
        image=Image.new("RGB", (1, 1)), name="image", location_path=location_path
    )
    with pytest.raises(ValueError, match="Unsafe ZIP member"):
        with ImageZipTerminus(output_path) as terminus:
            terminus(image)
    assert list(tmp_path.iterdir()) == []
