#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of ImageDirectorySource."""

from pytest import mark

from pipescaler.core.pipelines import Source
from pipescaler.image.pipelines.sources import ImageDirectorySource
from pipescaler.testing.file import get_test_input_dir_path


@mark.parametrize(
    "source",
    [
        (ImageDirectorySource(get_test_input_dir_path("basic"))),
    ],
)
def test(source: Source):
    """Test ImageDirectorySource loading images from directory.

    Arguments:
        source: ImageDirectorySource instance to test
    """
    for image in source:
        assert image.parents is None
