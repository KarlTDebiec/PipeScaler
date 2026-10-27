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

    if merger.palette_match_mode == PaletteMatchMode.LOCAL:
        fit_img = fit_img.resize((ref_img.width * 2, ref_img.height * 2))
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
@pytest.mark.parametrize("scale", [2, 3])
def test_local_match_integer_upscale(mode: str, scale: int):
    """Local matching preserves an exact uniform integer upscale.

    Arguments:
        mode: image mode to match
        scale: integer enlargement factor
    """
    ref_arr = np.array([[10, 50, 90], [130, 170, 210]], dtype=np.uint8)
    if mode == "RGB":
        ref_arr = np.repeat(ref_arr[:, :, np.newaxis], 3, axis=2)
    fit_arr = np.repeat(np.repeat(ref_arr, scale, axis=0), scale, axis=1)
    merger = PaletteMatchMerger(palette_match_mode=PaletteMatchMode.LOCAL)

    matched = merger(Image.fromarray(ref_arr), Image.fromarray(fit_arr))

    np.testing.assert_array_equal(np.asarray(matched), fit_arr)


@pytest.mark.parametrize("mode", ["L", "RGB"])
@pytest.mark.parametrize(
    ("ref_size", "fit_size"),
    [
        ((4, 4), (2, 2)),
        ((2, 3), (2, 3)),
        ((3, 3), (5, 5)),
        ((2, 3), (4, 9)),
        ((2, 3), (4, 7)),
        ((2, 3), (5, 6)),
        ((2, 3), (4, 3)),
        ((0, 3), (4, 6)),
        ((2, 0), (4, 6)),
        ((2, 3), (0, 0)),
    ],
)
def test_local_match_rejects_invalid_geometry(
    mode: str, ref_size: tuple[int, int], fit_size: tuple[int, int]
):
    """Local matching rejects unsupported geometry before entering numeric kernels.

    Arguments:
        mode: image mode to match
        ref_size: reference image width and height
        fit_size: target image width and height
    """
    ref_img = Image.new(mode, ref_size)
    fit_img = Image.new(mode, fit_size)
    merger = PaletteMatchMerger(palette_match_mode=PaletteMatchMode.LOCAL)

    with pytest.raises(ValueError, match="uniform integer upscale"):
        LocalPaletteMatcher.run(ref_img, fit_img)
    with pytest.raises(ValueError, match="uniform integer upscale"):
        merger(ref_img, fit_img)


@pytest.mark.parametrize("mode", ["L", "RGB"])
def test_basic_match_allows_unrelated_sizes(mode: str):
    """Basic matching draws from the global palette regardless of image sizes.

    Arguments:
        mode: image mode to match
    """
    matched = PaletteMatchMerger()(Image.new(mode, (3, 5)), Image.new(mode, (2, 4)))

    assert matched.size == (2, 4)
