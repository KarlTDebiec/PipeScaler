#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for mask-filling backend selection, fallback, and palette matching."""

from __future__ import annotations

from logging import WARNING
from unittest.mock import patch

import numpy as np
import pytest
from PIL import Image

from pipescaler.image.core.enums import MaskFillMode
from pipescaler.image.core.exceptions import UnsupportedImageModeError
from pipescaler.image.utilities.mask_filler import MaskFiller, MaskFillError
from pipescaler.image.utilities.palette_matcher import PaletteMatcher


@pytest.mark.parametrize("mode", ["L", "RGB"])
@pytest.mark.parametrize("fill_mode", list(MaskFillMode))
def test_shader_fallback(
    mode: str,
    fill_mode: MaskFillMode,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
):
    """Preserve complete CPU results when GPU execution fails.

    Arguments:
        mode: image mode to fill
        fill_mode: basic filling or subsequent palette matching
        monkeypatch: fixture for forcing shader selection
        caplog: captured fallback diagnostics
    """
    rng = np.random.default_rng(792)
    shape = (9, 17) if mode == "L" else (9, 17, 3)
    image = Image.fromarray(rng.integers(0, 256, shape, dtype=np.uint8))
    mask = Image.fromarray(rng.random((9, 17)) < 0.65)
    expected = MaskFiller.run(image, mask, fill_mode)
    monkeypatch.setattr(MaskFiller, "_minimum_shader_pixels", 0)

    with patch.object(
        MaskFiller, "_run_gpu", side_effect=MaskFillError("forced failure")
    ) as shader:
        actual = MaskFiller.run(image, mask, fill_mode)

    shader.assert_called_once()
    np.testing.assert_array_equal(np.asarray(actual), np.asarray(expected))
    (warning_record,) = caplog.records
    assert warning_record.name == MaskFiller.__module__
    assert warning_record.levelno == WARNING
    assert "forced failure" in warning_record.getMessage()


@pytest.mark.parametrize("mode", ["L", "RGB"])
@pytest.mark.parametrize("fill_mode", list(MaskFillMode))
def test_large_masks_use_shader(mode: str, fill_mode: MaskFillMode):
    """Use shader results and apply the requested palette-matching stage.

    Arguments:
        mode: image mode to fill
        fill_mode: basic filling or subsequent palette matching
    """
    values = np.zeros((40, 40), dtype=np.uint8)
    values[0, :] = 255
    image = Image.fromarray(values).convert(mode)
    mask = Image.fromarray(np.indices(values.shape)[0] > 0)
    filled = Image.new("L", image.size, 191).convert(mode)
    expected = filled
    if fill_mode == MaskFillMode.MATCH_PALETTE:
        expected = PaletteMatcher.run(image, filled)

    with (
        patch.object(MaskFiller, "_run_gpu", return_value=filled) as shader,
        patch.object(MaskFiller, "run_iteration", side_effect=AssertionError),
    ):
        actual = MaskFiller.run(image, mask, fill_mode)

    shader.assert_called_once()
    np.testing.assert_array_equal(np.asarray(actual), np.asarray(expected))


@pytest.mark.parametrize("size", [(9, 7), (128, 128)])
def test_small_masks_avoid_gpu_overhead(size: tuple[int, int]):
    """Keep single-pixel fills on the CPU even when the image is large.

    Arguments:
        size: dimensions of the image containing a sparse mask
    """
    image = Image.new("L", size, 37)
    mask = Image.new("1", size)
    mask.putpixel((1, 1), 1)
    image.putpixel((1, 1), 0)
    with patch.object(MaskFiller, "_run_gpu", side_effect=AssertionError):
        actual = MaskFiller.run(image, mask, MaskFillMode.BASIC)

    assert actual.getpixel((1, 1)) == 37


@pytest.mark.parametrize("fill_mode", list(MaskFillMode))
@pytest.mark.parametrize("masked", [False, True])
def test_trivial_masks_skip_processing(fill_mode: MaskFillMode, masked: bool):
    """Preserve unfillable or unmasked images without loading compute pipelines.

    Arguments:
        fill_mode: basic filling or subsequent palette matching
        masked: whether all pixels are masked
    """
    image = Image.new("L", (40, 40), 73)
    with (
        patch.object(MaskFiller, "_run_gpu", side_effect=AssertionError),
        patch.object(PaletteMatcher, "run", side_effect=AssertionError),
    ):
        actual = MaskFiller.run(
            image, Image.new("1", image.size, int(masked)), fill_mode
        )

    assert actual is not image
    assert actual.tobytes() == image.tobytes()


@pytest.mark.parametrize(("image_mode", "mask_mode"), [("RGBA", "1"), ("L", "L")])
def test_rejects_unsupported_modes(image_mode: str, mask_mode: str):
    """Validate modes consistently before selecting a backend.

    Arguments:
        image_mode: image mode to reject
        mask_mode: mask mode to reject
    """
    with pytest.raises(UnsupportedImageModeError, match="Mask filling requires"):
        MaskFiller.run(
            Image.new(image_mode, (2, 2)),
            Image.new(mask_mode, (2, 2)),
            MaskFillMode.BASIC,
        )


def test_rejects_mismatched_sizes():
    """Validate dimensions consistently before selecting a backend."""
    with pytest.raises(ValueError, match="matching image and mask sizes"):
        MaskFiller.run(
            Image.new("L", (2, 3)), Image.new("1", (3, 2)), MaskFillMode.BASIC
        )
