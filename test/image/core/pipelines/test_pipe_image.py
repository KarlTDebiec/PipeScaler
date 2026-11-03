#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for detached pipeline image loading."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image
from PIL.ImageFile import ImageFile

from pipescaler.image.core.pipelines import PipeImage


def test_default_file_loading_remains_lazy(tmp_path: Path):
    """Retain Pillow's lazy metadata and file-format behavior by default.

    Arguments:
        tmp_path: temporary image directory
    """
    path = tmp_path / "image.png"
    Image.new("RGB", (2, 3), "red").save(path)
    image = PipeImage(path=path)
    with image.image as loaded:
        assert loaded.size == (2, 3)
        assert loaded.format == "PNG"
        assert isinstance(loaded, ImageFile)
        assert loaded.fp is not None
        assert image.path == path


def test_detached_multiframe_image(tmp_path: Path):
    """Release an animated GIF's file while retaining its decoded first frame.

    Arguments:
        tmp_path: temporary image directory
    """
    path = tmp_path / "image.gif"
    Image.new("RGB", (2, 3), "red").save(
        path, save_all=True, append_images=[Image.new("RGB", (2, 3), "blue")]
    )
    image = PipeImage(path=path, detach_file=True)
    loaded = image.image
    path.unlink()
    assert loaded.getpixel((0, 0)) == (255, 0, 0)


def test_detachment_preserves_in_memory_input():
    """Retain an in-memory input's identity when no file needs detaching."""
    pixels = Image.new("RGB", (2, 3), "red")
    image = PipeImage(image=pixels, name="image", detach_file=True)
    assert image.image is pixels


@pytest.mark.parametrize("image_format", ["BMP", "PNG", "TIFF"])
def test_detached_image_releases_file(tmp_path: Path, image_format: str):
    """Keep decoded pixels while releasing files, including memory maps.

    Arguments:
        tmp_path: temporary image directory
        image_format: file format to load and detach
    """
    path = tmp_path / f"image.{image_format.lower()}"
    Image.new("L", (2, 3), 123).save(path, format=image_format)
    image = PipeImage(path=path, detach_file=True)
    loaded = image.image
    assert loaded.size == (2, 3)
    assert image.path == path
    path.unlink()
    assert loaded.getpixel((0, 0)) == 123
    assert image.image is loaded
