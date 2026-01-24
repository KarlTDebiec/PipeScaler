#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for MonochromeSorter."""

import pytest

from pipescaler.image.core.pipelines import PipeImage
from pipescaler.image.pipelines.sorters import MonochromeSorter
from pipescaler.testing.file import get_test_input_path
from pipescaler.testing.fixture import parametrized_fixture


@parametrized_fixture(
    cls=MonochromeSorter,
    params=[
        {"mean_threshold": 1, "max_threshold": 10},
    ],
)
def sorter(request) -> MonochromeSorter:
    """Pytest fixture that provides a MonochromeSorter instance.

    Arguments:
        request: Pytest request fixture containing parameters
    Returns:
        Configured MonochromeSorter instance
    """
    return MonochromeSorter(**request.param)


@pytest.mark.parametrize(
    ("input_filename", "outlet"),
    [
        ("1", "no_gray"),
        ("extra/1_L", "drop_gray"),
        ("L", "keep_gray"),
    ],
)
def test(input_filename: str, outlet: str, sorter: MonochromeSorter):
    """Test MonochromeSorter routing images based on monochrome properties.

    Arguments:
        input_filename: Input image filename
        outlet: Expected outlet name for routing
        sorter: MonochromeSorter fixture instance
    """
    img = PipeImage(path=get_test_input_path(input_filename))

    assert sorter(img) == outlet
