#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Functions for testing"""
from __future__ import annotations

from pipescaler.testing.file import (
    get_infile,
    get_model_infile,
    get_script,
    get_sub_directory,
)
from pipescaler.testing.fixture import stage_fixture
from pipescaler.testing.image import expected_output_mode
from pipescaler.testing.mark import (
    skip_if_ci,
    xfail_file_not_found,
    xfail_if_platform,
    xfail_unsupported_image_mode,
    xfail_value,
)

__all__: list[str] = [
    "expected_output_mode",
    "get_infile",
    "get_model_infile",
    "get_script",
    "get_sub_directory",
    "skip_if_ci",
    "stage_fixture",
    "xfail_file_not_found",
    "xfail_if_platform",
    "xfail_unsupported_image_mode",
    "xfail_value",
]
