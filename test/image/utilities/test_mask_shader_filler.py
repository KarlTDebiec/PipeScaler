#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for exact GPU mask filling and unavailable compute runtimes."""

from __future__ import annotations

from unittest.mock import patch

import numpy as np
import pytest
from PIL import Image
from wgpu.utils import get_default_device

from pipescaler.image.core.enums import MaskFillMode
from pipescaler.image.core.exceptions import UnsupportedImageModeError
from pipescaler.image.utilities.mask_filler import MaskFiller
from pipescaler.image.utilities.mask_shader_filler import (
    MaskShaderError,
    MaskShaderFiller,
)


@pytest.fixture
def shader_device():
    """Require a compute adapter for real shader execution tests."""
    try:
        get_default_device()
    except RuntimeError as exc:
        pytest.skip(f"No compute device available: {exc}")


@pytest.mark.usefixtures("shader_device")
@pytest.mark.parametrize("mode", ["L", "RGB"])
@pytest.mark.parametrize("size", [(1, 9), (9, 1), (7, 5), (17, 9)])
@pytest.mark.parametrize("seed", [0, 792, 2026])
def test_matches_cpu(mode: str, size: tuple[int, int], seed: int):
    """Match CPU priorities and rounding across image edges and random masks.

    Arguments:
        mode: image mode to fill
        size: image dimensions, including partial workgroups and singleton axes
        seed: reproducible pixel and mask seed
    """
    rng = np.random.default_rng(seed)
    width, height = size
    shape = (height, width) if mode == "L" else (height, width, 3)
    image = Image.fromarray(rng.integers(0, 256, shape, dtype=np.uint8))
    mask = Image.fromarray(rng.random((height, width)) < 0.65)
    before = image.tobytes(), mask.tobytes()

    expected = MaskFiller.run(image, mask, MaskFillMode.BASIC)
    actual = MaskShaderFiller.run(image, mask)

    assert actual.mode == mode
    assert actual.size == size
    assert (image.tobytes(), mask.tobytes()) == before
    np.testing.assert_array_equal(np.asarray(actual), np.asarray(expected))


@pytest.mark.usefixtures("shader_device")
@pytest.mark.parametrize("batch_size", [1, 7, 32])
@pytest.mark.parametrize("single_seed", [False, True])
def test_deep_masks_across_batches(
    batch_size: int, single_seed: bool, monkeypatch: pytest.MonkeyPatch
):
    """Preserve exact filling when many rounds cross readback boundaries.

    Arguments:
        batch_size: rounds submitted before checking progress
        single_seed: fill outward from one seed instead of into an interior hole
        monkeypatch: fixture for controlling the progress-readback interval
    """
    monkeypatch.setattr(MaskShaderFiller, "_rounds_per_batch", batch_size)
    rng = np.random.default_rng(792)
    image = Image.fromarray(rng.integers(0, 256, (19, 23, 3), dtype=np.uint8))
    mask_arr = np.ones((19, 23), dtype=bool)
    if single_seed:
        mask_arr[9, 11] = False
    else:
        mask_arr[[0, -1], :] = False
        mask_arr[:, [0, -1]] = False
    mask = Image.fromarray(mask_arr)

    expected = MaskFiller.run(image, mask, MaskFillMode.BASIC)
    actual = MaskShaderFiller.run(image, mask)

    np.testing.assert_array_equal(np.asarray(actual), np.asarray(expected))


@pytest.mark.usefixtures("shader_device")
@pytest.mark.parametrize("mode", ["L", "RGB"])
def test_same_round_pixels_do_not_feed_each_other(mode: str):
    """Average exclusively from pixels unmasked before the current round.

    Arguments:
        mode: image mode to fill
    """
    image = Image.fromarray(np.array([[0, 64, 192, 255]], dtype=np.uint8)).convert(mode)
    mask = Image.fromarray(np.array([[False, True, True, False]]))
    expected = Image.fromarray(np.array([[0, 0, 255, 255]], dtype=np.uint8)).convert(
        mode
    )

    actual = MaskShaderFiller.run(image, mask)

    np.testing.assert_array_equal(np.asarray(actual), np.asarray(expected))


@pytest.mark.usefixtures("shader_device")
@pytest.mark.parametrize("mode", ["L", "RGB"])
@pytest.mark.parametrize("fill_mode", list(MaskFillMode))
def test_integrated_large_fill_matches_cpu(mode: str, fill_mode: MaskFillMode):
    """Match the full CPU operation when normal selection chooses real WGSL.

    Arguments:
        mode: image mode to fill
        fill_mode: basic filling or subsequent palette matching
    """
    rng = np.random.default_rng(792)
    shape = (37, 41) if mode == "L" else (37, 41, 3)
    image = Image.fromarray(rng.integers(0, 256, shape, dtype=np.uint8))
    mask_arr = np.ones((37, 41), dtype=bool)
    mask_arr[[0, -1], :] = False
    mask_arr[:, [0, -1]] = False
    mask = Image.fromarray(mask_arr)
    with patch.object(MaskFiller, "_minimum_shader_pixels", mask_arr.size + 1):
        expected = MaskFiller.run(image, mask, fill_mode)

    with patch.object(MaskFiller, "run_iteration", side_effect=AssertionError):
        actual = MaskFiller.run(image, mask, fill_mode)

    np.testing.assert_array_equal(np.asarray(actual), np.asarray(expected))


@pytest.mark.parametrize("mode", ["L", "RGB"])
@pytest.mark.parametrize("size", [(0, 3), (1, 1), (9, 7)])
@pytest.mark.parametrize("masked", [False, True])
def test_trivial_masks_do_not_load_runtime(
    mode: str, size: tuple[int, int], masked: bool
):
    """Return unchanged pixels for empty, unmasked, and fully masked inputs.

    Arguments:
        mode: image mode to fill
        size: input dimensions
        masked: whether every pixel is masked
    """
    image = Image.new(mode, size, 73)
    mask = Image.new("1", size, int(masked))
    with patch.object(MaskShaderFiller, "_get_runtime", side_effect=AssertionError):
        actual = MaskShaderFiller.run(image, mask)

    assert actual is not image
    assert actual.mode == mode
    assert actual.size == size
    assert actual.tobytes() == image.tobytes()


@pytest.mark.parametrize(
    "error", [ModuleNotFoundError, ImportError, OSError, RuntimeError]
)
def test_runtime_load_failure(error: type[Exception]):
    """Expose missing modules and native failures as recoverable shader errors.

    Arguments:
        error: exception raised while importing the compute runtime
    """
    MaskShaderFiller._get_runtime.cache_clear()
    failure = error("runtime unavailable")
    mask = Image.new("1", (2, 1))
    mask.putpixel((0, 0), 1)
    with (
        patch(
            "pipescaler.image.utilities.mask_shader_filler.import_module",
            side_effect=failure,
        ),
        pytest.raises(MaskShaderError) as raised,
    ):
        MaskShaderFiller.run(Image.new("L", mask.size), mask)

    assert raised.value.__cause__ is failure


@pytest.mark.parametrize(("image_mode", "mask_mode"), [("RGBA", "1"), ("L", "L")])
def test_rejects_unsupported_modes(image_mode: str, mask_mode: str):
    """Reject invalid modes before constructing compute buffers.

    Arguments:
        image_mode: image mode to reject
        mask_mode: mask mode to reject
    """
    with pytest.raises(UnsupportedImageModeError, match="Mask filling requires"):
        MaskShaderFiller.run(
            Image.new(image_mode, (2, 2)), Image.new(mask_mode, (2, 2))
        )


def test_rejects_mismatched_sizes():
    """Reject mask dimensions that could cause out-of-bounds shader accesses."""
    with pytest.raises(ValueError, match="matching image and mask sizes"):
        MaskShaderFiller.run(Image.new("L", (2, 3)), Image.new("1", (3, 2)))
