#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for MonochromeSorter."""

from __future__ import annotations

import pytest
from PIL import Image

from pipescaler.image.core.pipelines import PipeImage
from pipescaler.image.pipelines.sorters import MonochromeSorter
from pipescaler.testing.file import get_test_input_path
from pipescaler.testing.fixture import parametrized_fixture


@parametrized_fixture(
    cls=MonochromeSorter,
    params=[
        {"mean_threshold": 1, "proportion_threshold": 0.1},
    ],
)
def sorter(request: pytest.FixtureRequest) -> MonochromeSorter:
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


def test_configured_thresholds_change_routing():
    """Configured thresholds control monochrome routing."""
    image = Image.frombytes("L", (4, 1), bytes([0, 10, 0, 0]))
    obj = PipeImage(image=image, name="sample")

    assert (
        MonochromeSorter(mean_threshold=3, proportion_threshold=0.25)(obj)
        == "drop_gray"
    )
    assert (
        MonochromeSorter(mean_threshold=2, proportion_threshold=0.25)(obj)
        == "keep_gray"
    )
    assert (
        MonochromeSorter(mean_threshold=3, proportion_threshold=0.2)(obj) == "keep_gray"
    )


@pytest.mark.parametrize(
    "kwargs",
    [
        {"mean_threshold": -0.1},
        {"mean_threshold": 255.1},
        {"proportion_threshold": -0.1},
        {"proportion_threshold": 1.1},
    ],
)
def test_threshold_bounds(kwargs: dict[str, float]):
    """Threshold arguments are validated against their units.

    Arguments:
        kwargs: Threshold configuration with an out-of-range value
    """
    with pytest.raises(ValueError):
        MonochromeSorter(**kwargs)


def test_defaults_and_repr():
    """Defaults are reflected in a reconstructible representation."""
    sorter = MonochromeSorter()

    assert sorter.mean_threshold == 0
    assert sorter.proportion_threshold == 0
    assert (
        repr(sorter) == "MonochromeSorter(mean_threshold=0.0, proportion_threshold=0.0)"
    )
    assert repr(eval(repr(sorter), {"MonochromeSorter": MonochromeSorter})) == repr(
        sorter
    )
