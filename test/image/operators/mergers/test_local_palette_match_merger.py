#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for LocalPaletteMatchMerger."""

from __future__ import annotations

import numpy as np
import pytest
from PIL import Image

from pipescaler.image.core.functions import get_palette, remove_palette
from pipescaler.image.operators.mergers import LocalPaletteMatchMerger
from pipescaler.image.testing import (
    get_expected_output_mode,
    xfail_unsupported_image_mode,
)
from pipescaler.image.utilities import LocalPaletteMatcher, LocalPaletteShaderMatcher
from pipescaler.image.utilities.local_palette_shader_matcher import (
    LocalPaletteShaderError,
)
from pipescaler.testing.file import get_test_input_path
from pipescaler.testing.fixture import parametrized_fixture


@parametrized_fixture(
    cls=LocalPaletteMatchMerger,
    params=[
        {},
        {"local_range": 2},
    ],
)
def merger(request) -> LocalPaletteMatchMerger:
    """Pytest fixture that provides a LocalPaletteMatchMerger instance.

    Arguments:
        request: Pytest request fixture containing parameters
    Returns:
        Configured LocalPaletteMatchMerger instance
    """
    return LocalPaletteMatchMerger(**request.param)


@pytest.mark.parametrize(
    ("ref", "fit"),
    [
        ("PL", "L"),
        xfail_unsupported_image_mode()("PLA", "LA"),
        ("PRGB", "RGB"),
        xfail_unsupported_image_mode()("PRGBA", "RGBA"),
    ],
)
def test(ref: str, fit: str, merger: LocalPaletteMatchMerger):
    """Test LocalPaletteMatchMerger with reference and fit images.

    Arguments:
        ref: Reference image filename with palette
        fit: Image to fit to reference palette filename
        merger: LocalPaletteMatchMerger fixture instance
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


def test_shader_fallback(monkeypatch: pytest.MonkeyPatch):
    """Test fallback to CPU matching when shader matching fails."""
    ref_input_path = get_test_input_path("PRGB")
    fit_input_path = get_test_input_path("alt/RGB")
    with Image.open(ref_input_path) as ref_img, Image.open(fit_input_path) as fit_img:
        expected_img = LocalPaletteMatcher.run(
            remove_palette(ref_img),
            fit_img,
            local_range=2,
        )

        def raise_shader_error(*args, **kwargs):
            """Raise shader error."""
            raise LocalPaletteShaderError("forced shader failure")

        monkeypatch.setattr(LocalPaletteShaderMatcher, "run", raise_shader_error)
        merger = LocalPaletteMatchMerger(local_range=2)
        output_img = merger(ref_img, fit_img)
        assert np.array_equal(np.array(output_img), np.array(expected_img))


@pytest.mark.parametrize(
    "merger",
    [
        LocalPaletteMatchMerger(),
        LocalPaletteMatchMerger(local_range=2),
    ],
)
def test_repr_round_trip(merger: LocalPaletteMatchMerger):
    """Test LocalPaletteMatchMerger repr round-trip recreation."""
    recreated = eval(repr(merger))
    assert repr(recreated) == repr(merger)
