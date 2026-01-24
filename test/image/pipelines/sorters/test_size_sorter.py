#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for SizeSorter."""

import pytest

from pipescaler.image.core.pipelines import PipeImage
from pipescaler.image.pipelines.sorters import SizeSorter
from pipescaler.testing.file import get_test_input_path
from pipescaler.testing.fixture import parametrized_fixture


@parametrized_fixture(
    cls=SizeSorter,
    params=[
        {"cutoff": 128},
    ],
)
def sorter(request) -> SizeSorter:
    """Pytest fixture that provides a SizeSorter instance.

    Arguments:
        request: Pytest request fixture containing parameters
    Returns:
        Configured SizeSorter instance
    """
    return SizeSorter(**request.param)


@pytest.mark.parametrize(
    ("input_filename", "outlet"),
    [
        ("L", "greater_than_or_equal_to"),
    ],
)
def test(input_filename: str, outlet: str, sorter: SizeSorter):
    """Test SizeSorter routing images based on size thresholds.

    Arguments:
        input_filename: Input image filename
        outlet: Expected outlet name for routing
        sorter: SizeSorter fixture instance
    """
    img = PipeImage(path=get_test_input_path(input_filename))

    assert sorter(img) == outlet
