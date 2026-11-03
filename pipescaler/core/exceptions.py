#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared exceptions for PipeScaler domain failures."""

from __future__ import annotations

__all__ = ["PipeScalerError"]


class PipeScalerError(Exception):
    """Base for expected failures specific to PipeScaler operations.

    Catch this type to handle domain failures across image and video operations.
    General-purpose utility errors, built-in validation and programming errors,
    and pipeline control-flow signals remain outside this hierarchy.
    """
