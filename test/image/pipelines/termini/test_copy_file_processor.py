#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for CopyImageTerminus."""

from tempfile import TemporaryDirectory

from pipescaler.image.core.pipelines import PipeImage
from pipescaler.image.pipelines.termini import ImageDirectoryTerminus
from pipescaler.testing.file import get_test_input_dir_path


def test():
    """Test ImageDirectoryTerminus copying and managing image files."""
    with TemporaryDirectory() as output_dir_path:
        terminus = ImageDirectoryTerminus(dir_path=output_dir_path)

        for input_path in get_test_input_dir_path("basic").iterdir():
            terminus(PipeImage(path=input_path))
        for input_path in get_test_input_dir_path("basic").iterdir():
            terminus(PipeImage(path=input_path))
        for input_path in get_test_input_dir_path("alt").iterdir():
            terminus(PipeImage(path=input_path))

        terminus = ImageDirectoryTerminus(dir_path=output_dir_path)
        terminus.purge_unrecognized_files()
