#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for NormalMerger."""

from __future__ import annotations

import pytest
from PIL import Image

from pipescaler.image.core.exceptions import UnsupportedImageModeError
from pipescaler.image.operators.mergers import NormalMerger
from pipescaler.testing.file import get_test_input_path
from pipescaler.testing.fixture import parametrized_fixture


@parametrized_fixture(
    cls=NormalMerger,
    params=[
        {},
    ],
)
def merger(request: pytest.FixtureRequest) -> NormalMerger:
    """Pytest fixture that provides a NormalMerger instance.

    Arguments:
        request: Pytest request fixture containing parameters
    Returns:
        Configured NormalMerger instance
    """
    return NormalMerger(**request.param)


@pytest.mark.parametrize(
    ("x", "y", "z", "supported"),
    [
        ("split/RGB_normal_x_L", "split/RGB_normal_y_L", "split/RGB_normal_z_L", True),
        ("RGB", "L", "L", False),
        ("L", "RGB", "L", False),
        ("L", "L", "RGB", False),
        (
            "split/RGB_normal_x_PL",
            "split/RGB_normal_y_PL",
            "split/RGB_normal_z_PL",
            True,
        ),
    ],
)
def test(x: str, y: str, z: str, merger: NormalMerger, supported: bool):
    """Test NormalMerger with X, Y, and Z normal map channels.

    Arguments:
        x: X channel normal map filename
        y: Y channel normal map filename
        z: Z channel normal map filename
        merger: NormalMerger fixture instance
        supported: whether the input modes are accepted
    """
    x_input_path = get_test_input_path(x)
    x_img = Image.open(x_input_path)
    y_input_path = get_test_input_path(y)
    y_img = Image.open(y_input_path)
    z_input_path = get_test_input_path(z)
    z_img = Image.open(z_input_path)

    if not supported:
        with pytest.raises(
            UnsupportedImageModeError, match="is not among supported modes"
        ):
            merger(x_img, y_img, z_img)
        return
    output_img = merger(x_img, y_img, z_img)

    assert output_img.mode == "RGB"
    assert output_img.size == x_img.size == y_img.size == z_img.size
