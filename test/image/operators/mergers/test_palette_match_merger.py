#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for PaletteMatchMerger."""

from __future__ import annotations

import numpy as np
import pytest
from PIL import Image

from pipescaler.image.core import PaletteMatchMode
from pipescaler.image.core.functions import get_palette, remove_palette
from pipescaler.image.operators.mergers import PaletteMatchMerger
from pipescaler.image.testing import (
    get_expected_output_mode,
    xfail_unsupported_image_mode,
)
from pipescaler.image.utilities import LocalPaletteMatcher
from pipescaler.testing.file import get_test_input_path
from pipescaler.testing.fixture import parametrized_fixture


@parametrized_fixture(
    cls=PaletteMatchMerger,
    params=[
        {"palette_match_mode": PaletteMatchMode.BASIC},
        {"palette_match_mode": PaletteMatchMode.LOCAL},
    ],
)
def merger(request: pytest.FixtureRequest) -> PaletteMatchMerger:
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
        PaletteMatchMerger(palette_match_mode=PaletteMatchMode.LOCAL, local_range=2),
    ],
)
def test_repr_round_trip(merger: PaletteMatchMerger):
    """Test PaletteMatchMerger repr round-trip recreation.

    Arguments:
        merger: merger
    """
    recreated = eval(repr(merger))
    assert repr(recreated) == repr(merger)


@pytest.mark.parametrize("mode", ["L", "RGB"])
@pytest.mark.parametrize(
    ("ref_size", "fit_size"),
    [
        ((4, 4), (2, 2)),
        ((2, 2), (4, 4)),
        ((3, 5), (2, 4)),
        ((5, 3), (4, 2)),
        ((1, 4), (3, 1)),
        ((4, 1), (1, 3)),
    ],
)
def test_local_match_maps_fit_pixels_to_reference_coordinates(
    mode: str, ref_size: tuple[int, int], fit_size: tuple[int, int]
):
    """Local matching maps each fit coordinate proportionally to its reference.

    Arguments:
        mode: image mode to match
        ref_size: reference image width and height
        fit_size: fit image width and height
    """
    ref_width, ref_height = ref_size
    fit_width, fit_height = fit_size
    ref_l = np.fromfunction(
        lambda y, x: y * ref_width + x, (ref_height, ref_width), dtype=int
    ).astype(np.uint8)
    expected_l = np.fromfunction(
        lambda y, x: ref_l[
            (y.astype(int) * ref_height // fit_height),
            (x.astype(int) * ref_width // fit_width),
        ],
        (fit_height, fit_width),
        dtype=int,
    ).astype(np.uint8)
    if mode == "RGB":
        ref_arr = np.repeat(ref_l[:, :, np.newaxis], 3, axis=2)
        fit_arr = np.repeat(expected_l[:, :, np.newaxis], 3, axis=2)
    else:
        ref_arr = ref_l
        fit_arr = expected_l

    matched = LocalPaletteMatcher.run(
        Image.fromarray(ref_arr), Image.fromarray(fit_arr), local_range=0
    )

    np.testing.assert_array_equal(np.asarray(matched), fit_arr)
