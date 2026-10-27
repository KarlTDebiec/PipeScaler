#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for SpandrelProcessor."""

from __future__ import annotations

from typing import Any, cast

import numpy as np
import pytest
import torch
from PIL import Image

from pipescaler.common.file import get_temp_file_path
from pipescaler.image.operators.processors import SpandrelProcessor
from pipescaler.image.testing import (
    get_expected_output_mode,
)
from pipescaler.testing.file import get_test_input_path, get_test_model_path
from pipescaler.testing.mark import skip_if_ci, skip_if_codex


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


class _FakeModel:
    """Simple model mock for SpandrelProcessor initialization tests."""

    def __init__(self, input_channels: int = 3, output_channels: int = 3):
        """Initialize descriptor channel metadata.

        Arguments:
            input_channels: declared model input channel count
            output_channels: declared model output channel count
        """
        self.input_channels = input_channels
        self.output_channels = output_channels

    def eval(self):
        """Mock eval."""

    def to(self, _device: str) -> _FakeModel:
        """Mock device transfer.

        Arguments:
            _device:  device
        Returns:
            this model after selecting its device
        """
        return self


class _IdentityModel:
    """Return the input tensor unchanged."""

    def __call__(self, input_tensor: torch.Tensor) -> torch.Tensor:
        """Return the input tensor.

        Arguments:
            input_tensor: model input
        Returns:
            unchanged input tensor
        """
        return input_tensor


class _OutputModel:
    """Return a tensor with a configured shape."""

    def __init__(self, output_shape: tuple[int, int, int, int]):
        """Initialize the output shape.

        Arguments:
            output_shape: output tensor shape
        """
        self.output_shape = output_shape

    def __call__(self, _input_tensor: torch.Tensor) -> torch.Tensor:
        """Return a zero tensor with the configured shape.

        Arguments:
            _input_tensor: model input
        Returns:
            model output tensor
        """
        return torch.zeros(self.output_shape)


@pytest.mark.parametrize("size", [(4, 1), (1, 4), (1, 1)])
def test_spandrel_preserves_singleton_spatial_dimensions(size: tuple[int, int]):
    """Test one-row, one-column, and one-pixel RGB images.

    Arguments:
        size: image dimensions
    """
    processor = SpandrelProcessor.__new__(SpandrelProcessor)
    processor.device = "cpu"
    processor.model = cast(Any, _IdentityModel())
    input_arr = np.empty((size[1], size[0], 3), dtype=np.uint8)
    input_arr[:] = [19, 83, 211]
    input_image = Image.fromarray(input_arr)

    output_image = processor(input_image)
    output_arr = processor.upscale(np.asarray(input_image))

    assert output_image.size == size
    assert output_arr.shape == (size[1], size[0], 3)
    np.testing.assert_array_equal(np.asarray(output_image), input_arr)
    np.testing.assert_array_equal(output_arr, input_arr)


@pytest.mark.parametrize(
    ("output_shape", "error"),
    [((1, 1, 2, 2), r"shape \(1, 3, height, width\)"), ((1, 3, 0, 2), "non-empty")],
)
def test_spandrel_rejects_invalid_model_output(
    output_shape: tuple[int, int, int, int], error: str
):
    """Test model output channel and spatial shape validation.

    Arguments:
        output_shape: model output dimensions
        error: expected error message
    """
    processor = SpandrelProcessor.__new__(SpandrelProcessor)
    processor.device = "cpu"
    processor.model = cast(Any, _OutputModel(output_shape))

    with pytest.raises(ValueError, match=error):
        processor.upscale(np.zeros((2, 2, 3), dtype=np.uint8))


def test_spandrel_rejects_invalid_input_channels():
    """Test direct upscale rejects non-RGB arrays."""
    processor = SpandrelProcessor.__new__(SpandrelProcessor)
    processor.device = "cpu"
    processor.model = cast(Any, _IdentityModel())

    with pytest.raises(ValueError, match="HWC RGB"):
        processor.upscale(np.zeros((2, 2, 4), dtype=np.uint8))


@pytest.mark.parametrize(("input_channels", "output_channels"), [(1, 3), (3, 1)])
def test_rejects_incompatible_descriptor_channels(
    monkeypatch: pytest.MonkeyPatch, input_channels: int, output_channels: int
):
    """Test model loading rejects descriptors that do not support RGB.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        input_channels: declared model input channel count
        output_channels: declared model output channel count
    """
    monkeypatch.setattr(
        "pipescaler.image.operators.processors.spandrel_processor.ModelLoader.load_from_file",
        lambda *_args, **_kwargs: _FakeModel(input_channels, output_channels),
    )

    with get_temp_file_path(".pth") as model_path:
        model_path.touch()
        with pytest.raises(ValueError, match="descriptor reports"):
            SpandrelProcessor(model_input_path=model_path)


def test_repr_round_trip(monkeypatch: pytest.MonkeyPatch):
    """Test SpandrelProcessor repr round-trip recreation.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    monkeypatch.setattr(
        "pipescaler.image.operators.processors.spandrel_processor.ModelLoader.load_from_file",
        lambda *_args, **_kwargs: _FakeModel(),
    )

    with get_temp_file_path(".pth") as model_path:
        model_path.touch()
        processor = SpandrelProcessor(model_input_path=model_path)
        recreated = eval(
            repr(processor),
            {
                "Path": __import__("pathlib").Path,
                "SpandrelProcessor": SpandrelProcessor,
            },
        )
        assert recreated.model_input_path == processor.model_input_path
