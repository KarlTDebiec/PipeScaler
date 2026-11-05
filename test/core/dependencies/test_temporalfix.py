#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Optional TemporalFix dependencies stay lazy and explain missing runtimes."""

from __future__ import annotations

import sys
from collections.abc import Callable
from subprocess import run
from types import ModuleType
from unittest.mock import Mock

import pytest

from pipescaler.core.dependencies.temporalfix import (
    import_vapoursynth,
    import_vs_temporalfix,
    import_vs_temporalfix_arch,
    import_vs_temporalfix_utils,
)
from pipescaler.core.exceptions import DependencyError, PipeScalerError


@pytest.mark.parametrize(
    "importer",
    [
        import_vapoursynth,
        import_vs_temporalfix,
        import_vs_temporalfix_arch,
        import_vs_temporalfix_utils,
    ],
)
def test_missing_dependency(
    monkeypatch: pytest.MonkeyPatch, importer: Callable[[], ModuleType]
):
    """Preserve the import failure and explain which worker dependencies are needed.

    Arguments:
        monkeypatch: fixture for simulating an unavailable dependency
        importer: optional dependency loader
    """
    failure = ModuleNotFoundError("Optional dependency is unavailable")
    with monkeypatch.context() as patch:
        patch.setattr("builtins.__import__", Mock(side_effect=failure))
        with pytest.raises(DependencyError) as error:
            importer()
    assert isinstance(error.value, PipeScalerError)
    assert "pipescaler[temporalfix]" in str(error.value)
    assert error.value.__cause__ is failure


def test_runner_imports_without_native_dependencies():
    """Keep constructing a video runner independent of optional native packages."""
    run(
        [
            sys.executable,
            "-c",
            "import sys; "
            "sys.modules['vapoursynth'] = None; "
            "sys.modules['vs_temporalfix'] = None; "
            "from pipescaler.video.runners import TemporalFixRunner; "
            "from pipescaler.video.core.temporalfix_settings "
            "import TemporalFixSettings; "
            "TemporalFixRunner(TemporalFixSettings(matrix='709', color_range='full'))",
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
