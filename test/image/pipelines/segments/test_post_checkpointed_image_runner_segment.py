#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for atomic image runner checkpoints."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from shutil import copyfile

import pytest
from PIL import Image

from pipescaler.image.core.pipelines import PipeImage
from pipescaler.image.pipelines import ImageCheckpointManager


def test_partial_runner_failure_is_removed_and_retry_runs(
    tmp_path: Path,
):
    """Retry a runner after a partial output and exception.

    Arguments:
        tmp_path: temporary directory for input and checkpoints
    """
    manager = ImageCheckpointManager(tmp_path / "checkpoints")
    calls = 0

    def runner(input_path: Path, output_path: Path):
        """Fail partially once and copy valid input on retry.

        Arguments:
            input_path: runner input
            output_path: runner output
        Raises:
            RuntimeError: on the first invocation
        """
        nonlocal calls
        calls += 1
        if calls == 1:
            output_path.write_bytes(b"partial")
            raise RuntimeError("runner failed")
        copyfile(input_path, output_path)

    segment = manager.post_runner("processed.png")(runner)
    image = PipeImage(image=Image.new("RGB", (2, 2), "red"), name="source")

    with pytest.raises(RuntimeError, match="runner failed"):
        segment(image)

    checkpoint_path = manager.dir_path / "source" / "processed.png"
    assert not checkpoint_path.exists()
    assert not list(checkpoint_path.parent.iterdir())

    output = segment(image)[0]

    assert calls == 2
    assert output.path == checkpoint_path
    with Image.open(checkpoint_path) as saved_image:
        assert saved_image.getpixel((0, 0)) == (255, 0, 0)


@pytest.mark.parametrize("output_kind", ["malformed", "missing", "truncated"])
def test_invalid_runner_output_is_not_published(tmp_path: Path, output_kind: str):
    """Reject malformed or missing runner output and remove temporary files.

    Arguments:
        tmp_path: temporary directory for checkpoints
        output_kind: output behavior to exercise
    """
    extension = ".bmp" if output_kind == "truncated" else ".png"
    manager = ImageCheckpointManager(tmp_path / "checkpoints")

    def runner(input_path: Path, output_path: Path):
        """Produce the selected invalid runner output.

        Arguments:
            input_path: unused runner input
            output_path: runner output
        """
        if output_kind == "malformed":
            output_path.write_bytes(b"not an image")
        elif output_kind == "truncated":
            buffer = BytesIO()
            Image.new("RGB", (4, 4), "red").save(buffer, format="BMP")
            output_path.write_bytes(buffer.getvalue()[:-8])

    segment = manager.post_runner(f"processed{extension}")(runner)
    image = PipeImage(image=Image.new("RGB", (2, 2)), name="source")

    with pytest.raises((OSError, ValueError)):
        segment(image)

    checkpoint_path = manager.dir_path / "source" / f"processed{extension}"
    assert not checkpoint_path.exists()
    assert not list(checkpoint_path.parent.iterdir())


def test_runner_failure_preserves_existing_checkpoint(tmp_path: Path):
    """Keep a prior valid checkpoint when a replacement runner fails.

    Arguments:
        tmp_path: temporary directory for checkpoints
    """
    manager = ImageCheckpointManager(
        tmp_path / "checkpoints", validate_input_mtime=True
    )
    checkpoint_path = manager.dir_path / "source" / "processed.png"
    checkpoint_path.parent.mkdir(parents=True)
    Image.new("RGB", (1, 1), "blue").save(checkpoint_path)

    def runner(input_path: Path, output_path: Path):
        """Write partial bytes and fail.

        Arguments:
            input_path: unused runner input
            output_path: runner output
        Raises:
            RuntimeError: always
        """
        output_path.write_bytes(b"partial")
        raise RuntimeError("runner failed")

    segment = manager.post_runner("processed.png")(runner)
    image = PipeImage(image=Image.new("RGB", (2, 2)), name="source")

    with pytest.raises(RuntimeError, match="runner failed"):
        segment(image)

    with Image.open(checkpoint_path) as saved_image:
        assert saved_image.getpixel((0, 0)) == (0, 0, 255)
    assert len(list(checkpoint_path.parent.iterdir())) == 1


def test_pipe_image_save_failure_preserves_existing_file(tmp_path: Path):
    """Keep existing image bytes and path when a replacement save fails.

    Arguments:
        tmp_path: temporary directory for the image file
    """
    image_path = tmp_path / "image.png"
    Image.new("RGB", (1, 1), "green").save(image_path)
    image = PipeImage(path=image_path)
    prior_bytes = image_path.read_bytes()

    def failed_save(path: Path):
        """Write partial content then fail.

        Arguments:
            path: output path
        Raises:
            RuntimeError: always
        """
        path.write_bytes(b"partial")
        raise RuntimeError("save failed")

    setattr(image.image, "save", failed_save)

    with pytest.raises(RuntimeError, match="save failed"):
        image.save(image_path)

    assert image.path == image_path
    assert image_path.read_bytes() == prior_bytes
    assert list(tmp_path.iterdir()) == [image_path]


def test_pipe_image_save_publishes_valid_image(tmp_path: Path):
    """Publish successful saves and update the image path.

    Arguments:
        tmp_path: temporary directory for the image file
    """
    image = PipeImage(image=Image.new("RGB", (1, 1), "yellow"), name="image")
    image_path = tmp_path / "image.png"

    image.save(image_path)

    assert image.path == image_path.resolve()
    with Image.open(image_path) as saved_image:
        assert saved_image.getpixel((0, 0)) == (255, 255, 0)
