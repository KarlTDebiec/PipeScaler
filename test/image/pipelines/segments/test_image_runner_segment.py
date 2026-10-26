#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for temporary image runner output ownership."""

from __future__ import annotations

from pathlib import Path
from shutil import copyfile
from unittest.mock import Mock

import pytest
from PIL import Image

from pipescaler.image.core.pipelines import PipeImage
from pipescaler.image.pipelines.segments import ImageRunnerSegment


@pytest.mark.parametrize("file_backed", [False, True])
def test_output_pixels_survive_temporary_file_cleanup(
    tmp_path: Path, file_backed: bool
):
    """Retain output pixels while removing temporary files and preserving lineage.

    Arguments:
        tmp_path: temporary directory for source and final output
        file_backed: whether the input starts with a file or in-memory pixels
    """
    source_image = Image.new("RGBA", (3, 2), (10, 20, 30, 128))
    source_path = tmp_path / "source.png"
    if file_backed:
        source_image.save(source_path)
        input_obj = PipeImage(path=source_path)
    else:
        input_obj = PipeImage(image=source_image, name="source")
    runner = Mock(side_effect=copyfile)

    outputs = ImageRunnerSegment(runner)(input_obj)

    assert len(outputs) == 1
    output = outputs[0]
    assert output.path is None
    assert output.parents == [input_obj]
    assert output.name == input_obj.name
    assert output.image.mode == "RGBA"
    assert output.image.size == (3, 2)
    assert output.image.getpixel((0, 0)) == (10, 20, 30, 128)
    temporary_input_path, temporary_output_path = runner.call_args.args
    assert not temporary_output_path.exists()
    if not file_backed:
        assert not temporary_input_path.exists()
    output.save(tmp_path / "final.png")
    with Image.open(tmp_path / "final.png") as final_image:
        assert final_image.getpixel((0, 0)) == (10, 20, 30, 128)
