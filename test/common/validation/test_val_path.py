#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for path normalization without existence checks or filesystem writes."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from pipescaler.common.validation import val_path


def test_expands_home_and_environment(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Apply the same home and environment expansion to missing input templates.

    Arguments:
        tmp_path: temporary home directory
        monkeypatch: environment replacements
    """
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setenv("VIDEO_ROOT", str(tmp_path))
    expected_path = tmp_path / "frames" / "%06d.png"

    assert val_path("~/frames/%06d.png") == expected_path
    assert val_path("$VIDEO_ROOT/frames/%06d.png") == expected_path
    assert not expected_path.parent.exists()


@pytest.mark.parametrize("value", [None, 123, b"frames/%06d.png"])
def test_rejects_invalid_path_values(value: Any):
    """Reject unsupported values instead of converting them to filenames.

    Arguments:
        value: intentionally invalid path value
    """
    with pytest.raises(TypeError):
        val_path(value)


@pytest.mark.parametrize("as_string", [False, True])
def test_resolves_missing_template(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, as_string: bool
):
    """Resolve relative paths and parent components without creating directories.

    Arguments:
        tmp_path: temporary working directory
        monkeypatch: working directory replacement
        as_string: whether to pass a string instead of a Path
    """
    monkeypatch.chdir(tmp_path)
    input_path = Path("missing/../frames/%06d.png")
    value = str(input_path) if as_string else input_path

    assert val_path(value) == tmp_path / "frames" / "%06d.png"
    assert list(tmp_path.iterdir()) == []
