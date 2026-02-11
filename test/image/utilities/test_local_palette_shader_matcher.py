#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for LocalPaletteShaderMatcher."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
import pytest
from PIL import Image

from pipescaler.image.utilities.local_palette_shader_matcher import (
    LocalPaletteShaderMatcher,
)


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
        LocalPaletteShaderMatcher,
        "_get_compute_with_buffers",
        classmethod(lambda cls: mock_compute),
    )
    ref_img = Image.fromarray(np.array([[0, 64], [128, 255]], dtype=np.uint8))
    fit_img = Image.fromarray(np.array([[16, 80], [160, 240]], dtype=np.uint8))

    output_img = LocalPaletteShaderMatcher.run(
        ref_img=ref_img,
        fit_img=fit_img,
        local_range=LocalPaletteShaderMatcher._max_local_range + 1,
    )

    params = captured["params"]
    assert isinstance(params, np.ndarray)
    assert params[4] == LocalPaletteShaderMatcher._max_local_range
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
        LocalPaletteShaderMatcher,
        "_get_compute_with_buffers",
        classmethod(lambda cls: mock_compute),
    )
    ref_arr = np.zeros((9, 17, 3), dtype=np.uint8)
    fit_arr = np.full((9, 17, 3), 128, dtype=np.uint8)
    ref_img = Image.fromarray(ref_arr, mode="RGB")
    fit_img = Image.fromarray(fit_arr, mode="RGB")

    output_img = LocalPaletteShaderMatcher.run(ref_img=ref_img, fit_img=fit_img)

    dispatch_n = captured["dispatch_n"]
    assert dispatch_n == (3, 2, 1)
    assert output_img.mode == "RGB"
    assert output_img.size == fit_img.size


def test_run_rejects_non_positive_local_range():
    """Test that non-positive local range raises a ValueError."""
    ref_img = Image.fromarray(np.array([[0, 1], [2, 3]], dtype=np.uint8))
    fit_img = Image.fromarray(np.array([[3, 2], [1, 0]], dtype=np.uint8))

    with pytest.raises(ValueError, match="local_range must be >= 1"):
        LocalPaletteShaderMatcher.run(ref_img=ref_img, fit_img=fit_img, local_range=0)
