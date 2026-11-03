#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for NormalSplitter."""

from __future__ import annotations

import pytest
from PIL import Image

from pipescaler.image.core.exceptions import UnsupportedImageModeError
from pipescaler.image.operators.splitters import NormalSplitter
from pipescaler.testing.file import get_test_input_path
from pipescaler.testing.fixture import parametrized_fixture


@parametrized_fixture(
    cls=NormalSplitter,
    params=[
        {},
    ],
)
def splitter(request: pytest.FixtureRequest) -> NormalSplitter:
    """Pytest fixture that provides a NormalSplitter instance.

    Arguments:
        request: Pytest request fixture containing parameters
    Returns:
        Configured NormalSplitter instance
    """
    return NormalSplitter(**request.param)


@pytest.mark.parametrize(
    ("input_filename", "supported"),
    [
        ("1", False),
        ("L", False),
        ("LA", False),
        ("RGB", True),
        ("RGBA", False),
        ("PRGB", True),
        ("novel/RGB_normal", True),
    ],
)
def test(input_filename: str, splitter: NormalSplitter, supported: bool):
    """Test NormalSplitter with various normal map images.

    Arguments:
        input_filename: Input image filename
        splitter: NormalSplitter fixture instance
        supported: whether the input modes are accepted
    """
    input_path = get_test_input_path(input_filename)
    input_img = Image.open(input_path)
    if not supported:
        with pytest.raises(
            UnsupportedImageModeError, match="is not among supported modes"
        ):
            splitter(input_img)
        return
    x_img, y_img, z_img = splitter(input_img)

    assert x_img.mode == "L"
    assert x_img.size == input_img.size
    assert y_img.mode == "L"
    assert y_img.size == input_img.size
    assert z_img.mode == "L"
    assert z_img.size == input_img.size
