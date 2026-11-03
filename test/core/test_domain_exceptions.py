#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the shared domain exception boundary."""

from __future__ import annotations

import pytest

from pipescaler.common.exceptions import (
    ArgumentConflictError,
    DirectoryExistsError,
    DirectoryNotFoundError,
    ExecutableNotFoundError,
    GetterError,
    IsAFileError,
    NotAFileError,
    NotAFileOrDirectoryError,
    UnsupportedPlatformError,
)
from pipescaler.core import PipeScalerError
from pipescaler.core.pipelines.exceptions import TerminusReached
from pipescaler.image.core.exceptions import UnsupportedImageModeError
from pipescaler.image.utilities.mask_filler import MaskFillError
from pipescaler.image.utilities.palette_shader_matcher import PaletteShaderError


@pytest.mark.parametrize(
    "error_cls", [UnsupportedImageModeError, MaskFillError, PaletteShaderError]
)
def test_domain_failures_share_base(error_cls: type[PipeScalerError]):
    """Catch domain failures through the public base without losing their type.

    Arguments:
        error_cls: concrete domain failure to raise
    Raises:
        PipeScalerError: raised deliberately to verify both catch boundaries
    """
    failure = error_cls("operation failed")
    with pytest.raises(PipeScalerError) as raised:
        raise failure

    assert raised.value is failure
    assert type(raised.value) is error_cls
    assert str(raised.value) == "operation failed"
    with pytest.raises(error_cls):
        raise failure


@pytest.mark.parametrize(
    "error_cls",
    [
        ArgumentConflictError,
        DirectoryExistsError,
        DirectoryNotFoundError,
        ExecutableNotFoundError,
        GetterError,
        IsAFileError,
        NotAFileError,
        NotAFileOrDirectoryError,
        UnsupportedPlatformError,
        TerminusReached,
        ValueError,
        TypeError,
        OSError,
        RuntimeError,
        NotImplementedError,
    ],
)
def test_generic_errors_and_control_flow_remain_distinct(error_cls: type[Exception]):
    """Keep generic errors and pipeline signals outside the domain hierarchy.

    Arguments:
        error_cls: utility, validation, programming, or control-flow exception
    """
    assert not issubclass(error_cls, PipeScalerError)
