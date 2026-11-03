#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Regression coverage for native tracing controls and allocation cleanup."""

from __future__ import annotations

import ctypes as ct
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Literal
from unittest.mock import Mock

import numpy as np
import pytest
from PIL import Image
from reportlab.graphics.shapes import Path as DrawingPath

from pipescaler.image.operators.processors import PotraceProcessor
from pipescaler.image.utilities import potrace


@pytest.mark.parametrize(
    ("policy", "policy_code"),
    [
        ("black", 0),
        ("white", 1),
        ("left", 2),
        ("right", 3),
        ("minority", 4),
        ("majority", 5),
        ("random", 6),
    ],
)
def test_ambiguous_paths_match_executable(policy: str, policy_code: int):
    """Match original bottom-up tracing decisions, including nested paths.

    Arguments:
        policy: turn policy name used to select the executable's reference paths
        policy_code: corresponding native turn policy code
    """
    reference_path = (
        Path(__file__).resolve().parents[2] / "data" / "potrace" / "checkerboard.json"
    )
    reference = json.loads(reference_path.read_text(encoding="utf-8"))
    rings = reference["paths"][policy]
    expected = DrawingPath()
    for start, *points in rings:
        expected.moveTo(*start)
        for point in points:
            expected.lineTo(*point)
        expected.closePath()
    actual = potrace.trace_bitmap(
        np.asarray(reference["pixels"], dtype=np.uint8) <= 0.3 * 255,
        turdsize=0,
        turnpolicy=policy_code,
        alphamax=0,
        opticurve=True,
        opttolerance=0.2,
    )
    assert actual.operators == expected.operators
    np.testing.assert_allclose(actual.points, expected.points, atol=1e-6, rtol=0)


@pytest.mark.parametrize(
    "policy", ["black", "white", "left", "right", "minority", "majority", "random"]
)
def test_native_controls(
    monkeypatch: pytest.MonkeyPatch,
    policy: Literal[
        "black", "white", "left", "right", "minority", "majority", "random"
    ],
):
    """Forward each typed setting to the native tracing parameters.

    Arguments:
        monkeypatch: fixture for observing the native call
        policy: turn policy to map to its native code
    """
    library = potrace._import_libpotrace()
    trace = library.potrace_trace

    def check_params(params: Any, bitmap: Any) -> Any:
        """Inspect native arguments and delegate to the real library.

        Arguments:
            params: native parameter structure pointer
            bitmap: packed native bitmap pointer
        Returns:
            native trace state owned by the caller
        """
        settings = params._obj
        assert settings.turdsize == 3
        assert settings.turnpolicy == (
            "black",
            "white",
            "left",
            "right",
            "minority",
            "majority",
            "random",
        ).index(policy)
        assert settings.alphamax == 0.7
        assert settings.opticurve == 0
        assert settings.opttolerance == 0.4
        return trace(params, bitmap)

    monkeypatch.setattr(library, "potrace_trace", check_params)
    processor = PotraceProcessor(
        turdsize=3, turnpolicy=policy, alphamax=0.7, opticurve=False, opttolerance=0.4
    )
    assert processor(Image.new("L", (10, 10))).mode == "L"


@pytest.mark.parametrize("allocated", [False, True])
def test_native_failure_cleanup(monkeypatch: pytest.MonkeyPatch, allocated: bool):
    """Free incomplete native results, while leaving null allocations alone.

    Arguments:
        monkeypatch: fixture for simulating native allocation failures
        allocated: whether the library returns an incomplete state or null
    """
    state = potrace._State()
    state.status = 1
    if allocated:
        result = ct.pointer(state)
    else:
        result = ct.POINTER(potrace._State)()
    free = Mock()
    library = SimpleNamespace(
        potrace_trace=Mock(return_value=result), potrace_state_free=free
    )
    monkeypatch.setattr(potrace, "_import_libpotrace", lambda: library)
    with pytest.raises(MemoryError):
        potrace.trace_bitmap(
            np.zeros((4, 4), dtype=np.bool_),
            turdsize=2,
            turnpolicy=4,
            alphamax=1.34,
            opticurve=True,
            opttolerance=0.2,
        )
    assert free.call_count == int(allocated)


def test_missing_library(monkeypatch: pytest.MonkeyPatch):
    """Explain how to supply libpotrace when system discovery fails.

    Arguments:
        monkeypatch: fixture for hiding the installed library
    """
    monkeypatch.delenv("PIPESCALER_POTRACE_LIBRARY", raising=False)
    monkeypatch.setattr(potrace, "find_library", lambda name: None)
    potrace._import_libpotrace.cache_clear()
    try:
        with pytest.raises(OSError, match="PIPESCALER_POTRACE_LIBRARY"):
            potrace._import_libpotrace()
    finally:
        potrace._import_libpotrace.cache_clear()
