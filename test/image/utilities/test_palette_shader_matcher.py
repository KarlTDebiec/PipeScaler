#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for PaletteShaderMatcher."""

from __future__ import annotations

from collections.abc import Callable
from unittest.mock import patch

import numpy as np
import pytest
from PIL import Image
from wgpu.utils import get_default_device

from pipescaler.image.core import PaletteMatchMode
from pipescaler.image.utilities.local_palette_matcher import LocalPaletteMatcher
from pipescaler.image.utilities.palette_matcher import PaletteMatcher
from pipescaler.image.utilities.palette_shader_matcher import (
    PaletteShaderError,
    PaletteShaderMatcher,
)


@pytest.fixture
def shader_device():
    """Require an available compute device for shader execution tests."""
    try:
        get_default_device()
    except RuntimeError as exc:
        pytest.skip(f"No compute device available: {exc}")


@pytest.mark.parametrize(
    "error", [ModuleNotFoundError, ImportError, OSError, RuntimeError]
)
def test_runtime_load_failure_allows_cpu_fallback(error: type[Exception]):
    """Classify missing Python modules and native-library failures as unavailable.

    Arguments:
        error: runtime loading error exposed by the backend
    """
    failure = error("runtime unavailable")
    with (
        patch(
            "pipescaler.image.utilities.palette_shader_matcher.import_module",
            side_effect=failure,
        ),
        pytest.raises(PaletteShaderError) as raised,
    ):
        PaletteShaderMatcher.run(Image.new("L", (1, 1)), Image.new("L", (2, 2)))

    assert raised.value.__cause__ is failure


@pytest.mark.usefixtures("shader_device")
@pytest.mark.parametrize("mode", ["L", "RGB"])
@pytest.mark.parametrize("batch_size", [2, 65_536])
def test_basic_matches_cpu(mode: str, batch_size: int, monkeypatch: pytest.MonkeyPatch):
    """Match the global CPU result with unrelated sizes and bounded query batches.

    Arguments:
        mode: image mode to match
        batch_size: maximum unique colors dispatched together
        monkeypatch: fixture for reducing the batch size
    """
    monkeypatch.setattr(PaletteShaderMatcher, "_palette_batch_size", batch_size)
    rng = np.random.default_rng(792)
    ref_shape = (4, 3) if mode == "L" else (4, 3, 3)
    fit_shape = (3, 7) if mode == "L" else (3, 7, 3)
    ref_img = Image.fromarray(rng.integers(0, 256, ref_shape, dtype=np.uint8))
    fit_img = Image.fromarray(rng.integers(0, 256, fit_shape, dtype=np.uint8))

    expected = PaletteMatcher.run(ref_img, fit_img)
    actual = PaletteShaderMatcher.run(ref_img, fit_img)

    assert actual.mode == mode
    assert actual.size == fit_img.size
    np.testing.assert_array_equal(np.asarray(actual), np.asarray(expected))


@pytest.mark.usefixtures("shader_device")
@pytest.mark.parametrize("mode", ["L", "RGB"])
def test_basic_preserves_palette_tie_order(mode: str):
    """Keep the CPU reference-palette order when candidates are equidistant.

    Arguments:
        mode: image mode to match
    """
    reference = Image.fromarray(np.array([[2, 0, 2]], dtype=np.uint8)).convert(mode)
    target = Image.new("L", (2, 3), 1).convert(mode)

    expected = PaletteMatcher.run(reference, target)
    actual = PaletteShaderMatcher.run(reference, target)

    np.testing.assert_array_equal(np.asarray(actual), np.asarray(expected))


@pytest.mark.usefixtures("shader_device")
def test_basic_selects_closer_color_in_near_tie():
    """Use exact RGB distances for the global palette as well as local searches."""
    reference = Image.fromarray(
        np.array([[(72, 159, 216), (70, 160, 212)]], dtype=np.uint8)
    )
    target = Image.new("RGB", (3, 2), (49, 25, 174))

    actual = PaletteShaderMatcher.run(reference, target)

    np.testing.assert_array_equal(
        np.asarray(actual), np.full((2, 3, 3), (70, 160, 212), dtype=np.uint8)
    )


def test_basic_dispatches_unique_colors(monkeypatch: pytest.MonkeyPatch):
    """Transfer reference and target palettes instead of repeated image pixels.

    Arguments:
        monkeypatch: fixture for capturing the compute buffers
    """
    captured: dict[str, np.ndarray | tuple[int, int, int] | str] = {}
    monkeypatch.setattr(
        PaletteShaderMatcher,
        "_import_compute_with_buffers",
        classmethod(lambda cls: _mock_compute_with_buffers_factory(captured)),
    )
    reference = Image.fromarray(np.array([[0, 255, 0, 255]], dtype=np.uint8))
    target = Image.fromarray(np.array([[32, 64, 32], [64, 32, 64]], dtype=np.uint8))

    PaletteShaderMatcher.run(reference, target)

    params = captured["params"]
    assert isinstance(params, np.ndarray)
    np.testing.assert_array_equal(params, [1, 2, 1, 2, 0, 1])
    assert captured["dispatch_n"] == (1, 1, 1)


@pytest.mark.usefixtures("shader_device")
def test_run_selects_closer_color_in_near_tie():
    """Preserve the closer RGB candidate when float32 distances round together."""
    ref_arr = np.array([[(72, 159, 216), (70, 160, 212)]] * 2, dtype=np.uint8)
    fit_arr = np.full((4, 4, 3), (49, 25, 174), dtype=np.uint8)
    ref_img = Image.fromarray(ref_arr)
    fit_img = Image.fromarray(fit_arr)
    expected = np.full((4, 4, 3), (70, 160, 212), dtype=np.uint8)

    # Exact squared weighted distances multiplied by 512 are 39872125 and 39872123
    np.testing.assert_array_equal(
        np.asarray(LocalPaletteMatcher.run(ref_img, fit_img)), expected
    )
    np.testing.assert_array_equal(
        np.asarray(
            PaletteShaderMatcher.run(
                palette_match_mode=PaletteMatchMode.LOCAL,
                ref_img=ref_img,
                fit_img=fit_img,
            )
        ),
        expected,
    )


@pytest.mark.usefixtures("shader_device")
@pytest.mark.parametrize("mode", ["L", "RGB"])
@pytest.mark.parametrize("scale", [2, 3])
@pytest.mark.parametrize("local_range", [1, 2])
def test_run_matches_cpu(mode: str, scale: int, local_range: int):
    """Match CPU output across channels, scales, neighborhoods, and image edges.

    Arguments:
        mode: image mode to match
        scale: integer enlargement factor
        local_range: radius of the reference neighborhood
    """
    rng = np.random.default_rng(792)
    shape = (3, 5) if mode == "L" else (3, 5, 3)
    fit_shape = (3 * scale, 5 * scale) if mode == "L" else (3 * scale, 5 * scale, 3)
    ref_img = Image.fromarray(rng.integers(0, 256, shape, dtype=np.uint8))
    fit_img = Image.fromarray(rng.integers(0, 256, fit_shape, dtype=np.uint8))

    expected = LocalPaletteMatcher.run(ref_img, fit_img, local_range=local_range)
    actual = PaletteShaderMatcher.run(
        palette_match_mode=PaletteMatchMode.LOCAL,
        ref_img=ref_img,
        fit_img=fit_img,
        local_range=local_range,
    )

    np.testing.assert_array_equal(np.asarray(actual), np.asarray(expected))


@pytest.mark.usefixtures("shader_device")
@pytest.mark.parametrize("mode", ["L", "RGB"])
@pytest.mark.parametrize(
    ("reference_values", "target_value", "expected_value"),
    [([0, 2], 1, 0), ([255, 255], 0, 255), ([0, 0], 255, 0)],
)
def test_run_preserves_ties_and_extreme_distances(
    mode: str, reference_values: list[int], target_value: int, expected_value: int
):
    """Keep the first tied candidate and handle maximum byte-channel differences.

    Arguments:
        mode: image mode to match
        reference_values: grayscale values of the reference candidates
        target_value: grayscale value of the target image
        expected_value: grayscale value of the expected selected candidate
    """
    ref_img = Image.fromarray(np.array([reference_values] * 2, dtype=np.uint8))
    ref_img = ref_img.convert(mode)
    fit_img = Image.new("L", (4, 4), target_value).convert(mode)
    expected = Image.new("L", (4, 4), expected_value).convert(mode)

    actual = PaletteShaderMatcher.run(
        palette_match_mode=PaletteMatchMode.LOCAL, ref_img=ref_img, fit_img=fit_img
    )

    np.testing.assert_array_equal(np.asarray(actual), np.asarray(expected))


def _mock_compute_with_buffers_factory(
    captured: dict[str, np.ndarray | tuple[int, int, int] | str],
) -> Callable[..., dict[int, bytes]]:
    """Build a mock wgpu compute callback for shader matcher tests.

    Arguments:
        captured: mutable dictionary used to capture invocation data
    Returns:
        mock `compute_with_buffers` callback
    """

    def _compute_with_buffers(
        *,
        input_arrays: dict[int, np.ndarray],
        output_arrays: dict[int, int],
        shader: str,
        n: tuple[int, int, int],
    ) -> dict[int, bytes]:
        """Capture invocation arguments and return passthrough output bytes.

        Arguments:
            input_arrays: mapped input buffers for shader execution
            output_arrays: mapped output buffer sizes for shader execution
            shader: compiled WGSL shader source
            n: dispatched workgroup dimensions
        Returns:
            byte output for binding index `3`
        """
        captured["params"] = np.array(input_arrays[2], copy=True)
        captured["dispatch_n"] = n
        captured["shader"] = shader
        fit_flat = np.array(input_arrays[0], copy=True, dtype=np.uint32)
        expected_output_bytes = int(output_arrays[3])
        output_bytes = fit_flat.tobytes()
        assert len(output_bytes) == expected_output_bytes
        return {3: output_bytes}

    return _compute_with_buffers


def test_run_clamps_large_local_range_before_shader(monkeypatch: pytest.MonkeyPatch):
    """Test that large local_range values are clamped before shader invocation.

    Arguments:
        monkeypatch: pytest fixture for runtime monkeypatching
    """
    captured: dict[str, np.ndarray | tuple[int, int, int] | str] = {}
    mock_compute = _mock_compute_with_buffers_factory(captured)
    monkeypatch.setattr(
        PaletteShaderMatcher,
        "_import_compute_with_buffers",
        classmethod(lambda cls: mock_compute),
    )
    ref_img = Image.fromarray(np.array([[0, 64], [128, 255]], dtype=np.uint8))
    fit_img = Image.fromarray(np.array([[16, 80], [160, 240]], dtype=np.uint8))

    fit_img = fit_img.resize((ref_img.width * 2, ref_img.height * 2))
    output_img = PaletteShaderMatcher.run(
        palette_match_mode=PaletteMatchMode.LOCAL,
        ref_img=ref_img,
        fit_img=fit_img,
        local_range=PaletteShaderMatcher._max_local_range + 1,
    )

    params = captured["params"]
    assert isinstance(params, np.ndarray)
    assert params[4] == max(ref_img.size)
    assert output_img.mode == "L"
    assert output_img.size == fit_img.size


def test_run_uses_expected_workgroup_dispatch(monkeypatch: pytest.MonkeyPatch):
    """Test workgroup dispatch dimensions passed to shader compute backend.

    Arguments:
        monkeypatch: pytest fixture for runtime monkeypatching
    """
    captured: dict[str, np.ndarray | tuple[int, int, int] | str] = {}
    mock_compute = _mock_compute_with_buffers_factory(captured)
    monkeypatch.setattr(
        PaletteShaderMatcher,
        "_import_compute_with_buffers",
        classmethod(lambda cls: mock_compute),
    )
    ref_arr = np.zeros((9, 17, 3), dtype=np.uint8)
    fit_arr = np.full((9, 17, 3), 128, dtype=np.uint8)
    ref_img = Image.fromarray(ref_arr, mode="RGB")
    fit_img = Image.fromarray(fit_arr, mode="RGB")

    fit_img = fit_img.resize((ref_img.width * 2, ref_img.height * 2))
    output_img = PaletteShaderMatcher.run(
        palette_match_mode=PaletteMatchMode.LOCAL, ref_img=ref_img, fit_img=fit_img
    )

    dispatch_n = captured["dispatch_n"]
    assert dispatch_n == (5, 3, 1)
    assert output_img.mode == "RGB"
    assert output_img.size == fit_img.size


def test_run_rejects_non_positive_local_range():
    """Test that non-positive local range raises a ValueError."""
    ref_img = Image.fromarray(np.array([[0, 1], [2, 3]], dtype=np.uint8))
    fit_img = Image.fromarray(np.array([[3, 2], [1, 0]], dtype=np.uint8))

    with pytest.raises(ValueError, match="local_range must be >= 1"):
        PaletteShaderMatcher.run(
            palette_match_mode=PaletteMatchMode.LOCAL,
            ref_img=ref_img,
            fit_img=fit_img,
            local_range=0,
        )
