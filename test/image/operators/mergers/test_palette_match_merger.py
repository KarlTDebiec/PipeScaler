#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for PaletteMatchMerger."""

import pytest
from PIL import Image

from pipescaler.image.core.functions import get_palette, remove_palette
from pipescaler.image.operators.mergers import PaletteMatchMerger
from pipescaler.image.testing import (
    get_expected_output_mode,
    xfail_unsupported_image_mode,
)
from pipescaler.testing.file import get_test_input_path
from pipescaler.testing.fixture import parametrized_fixture


@parametrized_fixture(
    cls=PaletteMatchMerger,
    params=[
        {},
    ],
)
def merger(request) -> PaletteMatchMerger:
    """Pytest fixture that provides a PaletteMatchMerger instance.

    Arguments:
        request: Pytest request fixture containing parameters
    Returns:
        Configured PaletteMatchMerger instance
    """
    return PaletteMatchMerger(**request.param)


@pytest.mark.parametrize(
    ("ref", "fit"),
    [
        ("PL", "L"),
        xfail_unsupported_image_mode()("PLA", "LA"),
        ("PRGB", "RGB"),
        xfail_unsupported_image_mode()("PRGBA", "RGBA"),
    ],
)
def test(ref: str, fit: str, merger: PaletteMatchMerger):
    """Test PaletteMatchMerger with reference and fit images.

    Arguments:
        ref: Reference image filename with palette
        fit: Image to fit to reference palette filename
        merger: PaletteMatchMerger fixture instance
    """
    ref_input_path = get_test_input_path(ref)
    ref_img = Image.open(ref_input_path)
    fit_input_path = get_test_input_path(fit)
    fit_img = Image.open(fit_input_path)

    output_img = merger(ref_img, fit_img)

    if get_expected_output_mode(fit_img) == "L":
        ref_colors = set(get_palette(remove_palette(ref_img)))
        output_colors = set(get_palette(output_img))
    else:
        ref_colors = set(map(tuple, get_palette(remove_palette(ref_img))))
        output_colors = set(map(tuple, get_palette(output_img)))
    assert output_colors.issubset(ref_colors)
    assert output_img.mode == get_expected_output_mode(fit_img)
    assert output_img.size == fit_img.size


@pytest.mark.parametrize(
    "merger",
    [
        PaletteMatchMerger(),
    ],
)
def test_repr_round_trip(merger: PaletteMatchMerger):
    """Test PaletteMatchMerger repr round-trip recreation."""
    recreated = eval(repr(merger))
    assert repr(recreated) == repr(merger)
