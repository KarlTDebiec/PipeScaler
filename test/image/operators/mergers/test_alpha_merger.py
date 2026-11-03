#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for AlphaMerger."""

from __future__ import annotations

import pytest
from PIL import Image

from pipescaler.image.core.exceptions import UnsupportedImageModeError
from pipescaler.image.operators.mergers import AlphaMerger
from pipescaler.image.testing import get_expected_output_mode
from pipescaler.testing.file import get_test_input_path
from pipescaler.testing.fixture import parametrized_fixture


@parametrized_fixture(
    cls=AlphaMerger,
    params=[
        {},
    ],
)
def merger(request: pytest.FixtureRequest) -> AlphaMerger:
    """Pytest fixture that provides an AlphaMerger instance.

    Arguments:
        request: Pytest request fixture containing parameters
    Returns:
        Configured AlphaMerger instance
    """
    return AlphaMerger(**request.param)


@pytest.mark.parametrize(
    ("color", "alpha", "supported"),
    [
        ("split/LA_color_L", "split/LA_alpha_L", True),
        ("split/RGBA_color_RGB", "split/RGBA_alpha_L", True),
        ("split/RGBA_color_PRGB", "split/RGBA_alpha_PL", True),
        ("RGB", "RGB", False),
        ("RGB", "RGBA", False),
        ("RGBA", "L", False),
        ("split/LA_color_PL", "split/LA_alpha_PL", True),
        ("split/RGBA_monochrome_color_RGB", "split/RGBA_monochrome_alpha_1", True),
    ],
)
def test(color: str, alpha: str, merger: AlphaMerger, supported: bool):
    """Test AlphaMerger with various color and alpha channel combinations.

    Arguments:
        color: Color image filename
        alpha: Alpha channel image filename
        merger: AlphaMerger fixture instance
        supported: whether the input modes are accepted
    """
    color_input_path = get_test_input_path(color)
    color_img = Image.open(color_input_path)
    alpha_input_file = get_test_input_path(alpha)
    alpha_img = Image.open(alpha_input_file)

    if not supported:
        with pytest.raises(
            UnsupportedImageModeError, match="is not among supported modes"
        ):
            merger(color_img, alpha_img)
        return
    output_img = merger(color_img, alpha_img)

    if get_expected_output_mode(color_img) == "L":
        assert output_img.mode == "LA"
    else:
        assert output_img.mode == "RGBA"
    assert output_img.size == color_img.size
