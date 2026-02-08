#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for SpandrelProcessor."""

import pytest
from PIL import Image

from pipescaler.image.core.operators import ImageProcessor
from pipescaler.image.operators.processors import SpandrelProcessor
from pipescaler.image.testing import (
    get_expected_output_mode,
)
from pipescaler.testing.file import get_test_input_path, get_test_model_path
from pipescaler.testing.mark import skip_if_ci, skip_if_codex


def test_imageprocessor_interface():
    """Test that SpandrelProcessor conforms to ImageProcessor interface.

    This test validates that SpandrelProcessor properly inherits from
    ImageProcessor and implements the required interface methods without
    requiring the heavy dependencies (torch, spandrel, etc.).
    """
    # Verify inheritance
    assert issubclass(SpandrelProcessor, ImageProcessor)

    # Verify required class methods exist and return correct types
    inputs = SpandrelProcessor.inputs()
    outputs = SpandrelProcessor.outputs()

    assert isinstance(inputs, dict)
    assert isinstance(outputs, dict)
    assert "input" in inputs
    assert "output" in outputs

    # Verify the types of the tuples
    assert isinstance(inputs["input"], tuple)
    assert isinstance(outputs["output"], tuple)
    assert all(isinstance(mode, str) for mode in inputs["input"])
    assert all(isinstance(mode, str) for mode in outputs["output"])


@pytest.mark.serial
@pytest.mark.parametrize(
    ("input_filename", "model"),
    [
        # skip_if_codex(skip_if_ci())("1", "ESRGAN/1x_BC1-smooth2"),
        # skip_if_codex(skip_if_ci())("L", "ESRGAN/1x_BC1-smooth2"),
        # skip_if_codex(skip_if_ci(xfail_unsupported_image_mode()))(
        #     "LA", "ESRGAN/1x_BC1-smooth2"
        # ),
        # skip_if_codex(skip_if_ci(xfail_unsupported_image_mode()))(
        #     "RGBA", "ESRGAN/1x_BC1-smooth2"
        # ),
        # skip_if_codex(skip_if_ci())("RGB", "ESRGAN/1x_BC1-smooth2"),
        # skip_if_codex(skip_if_ci())("RGB", "ESRGAN/RRDB_ESRGAN_x4"),
        # skip_if_codex(skip_if_ci())("RGB", "ESRGAN/RRDB_ESRGAN_x4_old_arch"),
        skip_if_codex(skip_if_ci())("RGB", "DAT2/4x-PBRify_UpscalerV4"),
        # skip_if_codex(skip_if_ci())("PL", "ESRGAN/1x_BC1-smooth2"),
        # skip_if_codex(skip_if_ci(xfail_unsupported_image_mode()))(
        #     "PLA", "ESRGAN/1x_BC1-smooth2"
        # ),
        # skip_if_codex(skip_if_ci())("PRGB", "ESRGAN/1x_BC1-smooth2"),
        # skip_if_codex(skip_if_ci(xfail_unsupported_image_mode()))(
        #     "PRGBA", "ESRGAN/1x_BC1-smooth2"
        # ),
    ],
)
def test(input_filename: str, model: str):
    """Test SpandrelProcessor with various image modes and models.

    Arguments:
        input_filename: Input image filename
        model: Model path identifier
    """
    processor = SpandrelProcessor(model_input_path=get_test_model_path(model))

    input_path = get_test_input_path(input_filename)
    input_img = Image.open(input_path)
    output_img = processor(input_img)

    assert output_img.mode == get_expected_output_mode(input_img)
