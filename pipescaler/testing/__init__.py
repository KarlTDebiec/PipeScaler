#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Functions for testing."""
from __future__ import annotations

from pipescaler.testing.cli import run_cli_with_args
from pipescaler.testing.execution_counter import count_executions
from pipescaler.testing.file import (
    get_test_infile_directory_path,
    get_test_infile_path,
    get_test_model_infile_path,
)
from pipescaler.testing.fixture import parametrized_fixture
from pipescaler.testing.image import get_expected_output_mode
from pipescaler.testing.mark import (
    parametrize_with_readable_ids,
    skip_if_ci,
    xfail_file_not_found,
    xfail_if_platform,
    xfail_system_exit,
    xfail_unsupported_image_mode,
    xfail_value,
)

__all__: list[str] = [
    "count_executions",
    "get_expected_output_mode",
    "get_test_infile_directory_path",
    "get_test_infile_path",
    "get_test_model_infile_path",
    "parametrized_fixture",
    "parametrize_with_readable_ids",
    "run_cli_with_args",
    "skip_if_ci",
    "xfail_file_not_found",
    "xfail_if_platform",
    "xfail_system_exit",
    "xfail_unsupported_image_mode",
    "xfail_value",
]
