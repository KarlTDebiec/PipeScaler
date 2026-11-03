#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of ImageDirectorySource."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from pipescaler.image.pipelines.sources import ImageDirectorySource


def test_nested_images_preserve_content_and_identity(tmp_path: Path):
    """Yield every root and nested image with its pixels and relative identity.

    Arguments:
        tmp_path: temporary input directory
    """
    expected_colors = {
        Path("root.image.png"): (255, 0, 0),
        Path("nested/image.png"): (0, 255, 0),
        Path("nested/deeper/image.png"): (0, 0, 255),
    }
    for relative_path, color in expected_colors.items():
        input_path = tmp_path / relative_path
        input_path.parent.mkdir(parents=True, exist_ok=True)
        with Image.new("RGB", (3, 2), color) as input_image:
            input_image.putpixel((0, 0), (12, 34, 56))
            input_image.save(input_path)

    images = list(ImageDirectorySource(tmp_path))

    assert len(images) == 3
    assert {image.path for image in images} == {
        tmp_path / relative_path for relative_path in expected_colors
    }
    for image in images:
        assert image.path is not None
        relative_path = image.path.relative_to(tmp_path)
        assert image.name == relative_path.stem
        assert image.location == relative_path.parent
        assert image.location_name == str(relative_path.with_suffix(""))
        assert image.parents is None
        with image.image as pixels:
            assert pixels.mode == "RGB"
            assert pixels.size == (3, 2)
            assert pixels.getpixel((0, 0)) == (12, 34, 56)
            assert pixels.getpixel((2, 1)) == expected_colors[relative_path]
