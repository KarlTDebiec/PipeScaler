#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for EsrganSerializer."""

from __future__ import annotations

from pytest import fixture, mark

from pipescaler.common.file import get_temp_file_path
from pipescaler.image.utilities import EsrganSerializer
from pipescaler.testing.file import get_test_model_path
from pipescaler.testing.mark import skip_if_ci, skip_if_codex


@fixture
def utility(request) -> EsrganSerializer:
    """Pytest fixture that provides an EsrganSerializer instance.

    Arguments:
        request: Pytest request fixture
    Returns:
        Configured EsrganSerializer instance
    """
    return EsrganSerializer()


@mark.parametrize(
    "input_filename",
    [
        skip_if_codex(skip_if_ci())("ESRGAN/1x_BC1-smooth2"),
        skip_if_codex(skip_if_ci())("ESRGAN/RRDB_ESRGAN_x4"),
        skip_if_codex(skip_if_ci())("ESRGAN/RRDB_ESRGAN_x4_old_arch"),
    ],
)
def test(input_filename: str, utility: EsrganSerializer):
    """Test EsrganSerializer converting ESRGAN models to PyTorch format.

    Arguments:
        input_filename: Input model filename
        utility: EsrganSerializer fixture instance
    """
    input_path = get_test_model_path(input_filename)
    with get_temp_file_path(".pth") as output_path:
        utility.run(input_path, output_path)
