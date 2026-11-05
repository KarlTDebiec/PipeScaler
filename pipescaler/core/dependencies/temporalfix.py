#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
# ruff: noqa: PLC0415
"""Lazy access to optional TemporalFix dependencies."""

from __future__ import annotations

from types import ModuleType

from pipescaler.core.exceptions import DependencyError

__all__ = [
    "import_vapoursynth",
    "import_vs_temporalfix",
    "import_vs_temporalfix_arch",
    "import_vs_temporalfix_utils",
]

_TEMPORALFIX_SETUP_MESSAGE = (
    "TemporalFix requires optional video dependencies. Install "
    "pipescaler[temporalfix] in the calling Python environment with a native "
    "VapourSynth runtime."
)


def import_vapoursynth() -> ModuleType:
    """Import VapourSynth on demand.

    Returns:
        VapourSynth module
    Raises:
        DependencyError: if TemporalFix dependencies are unavailable
    """
    try:
        import vapoursynth
    except ImportError as exc:
        raise DependencyError(_TEMPORALFIX_SETUP_MESSAGE) from exc
    return vapoursynth


def import_vs_temporalfix() -> ModuleType:
    """Import vs_temporalfix on demand.

    Returns:
        vs_temporalfix module
    Raises:
        DependencyError: if TemporalFix dependencies are unavailable
    """
    try:
        import vs_temporalfix
    except ImportError as exc:
        raise DependencyError(_TEMPORALFIX_SETUP_MESSAGE) from exc
    return vs_temporalfix


def import_vs_temporalfix_arch() -> ModuleType:
    """Import the upstream TemporalFix architecture on demand.

    Returns:
        TemporalFix architecture module
    Raises:
        DependencyError: if TemporalFix dependencies are unavailable
    """
    try:
        from vs_temporalfix.models import temporalfix_arch
    except ImportError as exc:
        raise DependencyError(_TEMPORALFIX_SETUP_MESSAGE) from exc
    return temporalfix_arch


def import_vs_temporalfix_utils() -> ModuleType:
    """Import upstream TemporalFix utilities on demand.

    Returns:
        TemporalFix utility module
    Raises:
        DependencyError: if TemporalFix dependencies are unavailable
    """
    try:
        import vs_temporalfix.utils as temporalfix_utils
    except ImportError as exc:
        raise DependencyError(_TEMPORALFIX_SETUP_MESSAGE) from exc
    return temporalfix_utils
