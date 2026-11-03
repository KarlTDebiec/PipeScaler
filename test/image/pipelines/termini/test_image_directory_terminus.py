#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for ImageDirectoryTerminus."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from PIL import Image

from pipescaler.image.core.pipelines import PipeImage
from pipescaler.image.pipelines.termini import ImageDirectoryTerminus
from pipescaler.testing.file import get_test_input_dir_path


def test():
    """Test ImageDirectoryTerminus copying and managing image files."""
    with TemporaryDirectory() as output_dir_path:
        terminus = ImageDirectoryTerminus(dir_path=output_dir_path)

        for input_path in get_test_input_dir_path("basic").iterdir():
            terminus(PipeImage(path=input_path))
        for input_path in get_test_input_dir_path("basic").iterdir():
            terminus(PipeImage(path=input_path))
        for input_path in get_test_input_dir_path("alt").iterdir():
            terminus(PipeImage(path=input_path))

        terminus = ImageDirectoryTerminus(dir_path=output_dir_path)
        terminus.purge_unrecognized_files()


@pytest.mark.parametrize("file_backed", [False, True])
def test_preserves_dotted_names(tmp_path: Path, file_backed: bool):
    """Keep dotted image stems distinct in nested output directories.

    Arguments:
        tmp_path: temporary test directory
        file_backed: whether source images have an existing file path
    """
    terminus = ImageDirectoryTerminus(tmp_path / "output")
    colors = {"image.one": (255, 0, 0), "image.two": (0, 0, 255)}
    location_path = Path("nested.directory")
    for name, color in colors.items():
        image = Image.new("RGB", (2, 3), color)
        if file_backed:
            input_path = tmp_path / f"{name}.png"
            image.save(input_path)
            pipe_image = PipeImage(path=input_path, location_path=location_path)
        else:
            pipe_image = PipeImage(image=image, name=name, location_path=location_path)
        terminus(pipe_image)

    terminus.purge_unrecognized_files()
    output_dir_path = terminus.dir_path / location_path
    assert {path.name for path in output_dir_path.iterdir()} == {
        "image.one.png",
        "image.two.png",
    }
    for name, color in colors.items():
        with Image.open(output_dir_path / f"{name}.png") as output_image:
            assert output_image.size == (2, 3)
            assert output_image.tobytes() == Image.new("RGB", (2, 3), color).tobytes()


def test_modified_file_backed_image_is_saved_from_pixels(tmp_path: Path):
    """Save replacement pixels while preserving source, identity, and lineage.

    Arguments:
        tmp_path: temporary test directory
    """
    source_path = tmp_path / "source.png"
    original = Image.new("RGB", (2, 2), "red")
    original.save(source_path)
    parent = PipeImage(path=source_path, location_path=Path("nested"))
    image = parent.image.copy()
    image.paste("blue", (0, 0, 2, 2))
    parent.image = image

    terminus = ImageDirectoryTerminus(tmp_path / "output")
    terminus(parent)

    output_path = tmp_path / "output" / "nested" / "source.png"
    with Image.open(output_path) as output_image:
        assert output_image.getpixel((0, 0)) == (0, 0, 255)
    with Image.open(source_path) as source_image:
        assert source_image.getpixel((0, 0)) == (255, 0, 0)
    assert parent.path is None
    assert parent.name == "source"
    assert parent.location == Path("nested")
    assert parent.parents is None
