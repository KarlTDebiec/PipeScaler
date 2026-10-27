#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for the PyTorch image processor base class."""

from __future__ import annotations

import numpy as np
import pytest
import torch
from PIL import Image

from pipescaler.image.core.operators.processors import PyTorchImageProcessor


class _TestProcessor(PyTorchImageProcessor):
    """Concrete test processor that skips model loading."""


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


def _processor(model: object) -> _TestProcessor:
    """Create a test processor without loading an external model.

    Arguments:
        model: model to use for processing
    Returns:
        initialized processor with the given model
    """
    processor = _TestProcessor.__new__(_TestProcessor)
    processor.model = model
    processor.device = "cpu"
    return processor


@pytest.mark.parametrize("size", [(4, 1), (1, 4), (1, 1)])
def test_preserves_singleton_spatial_dimensions(size: tuple[int, int]):
    """Test one-row, one-column, and one-pixel RGB images.

    Arguments:
        size: image dimensions
    """
    processor = _processor(_IdentityModel())
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
    [
        ((1, 1, 2, 2), r"shape \(1, 3, height, width\)"),
        ((1, 3, 0, 2), "non-empty"),
    ],
)
def test_rejects_invalid_model_output(
    output_shape: tuple[int, int, int, int], error: str
):
    """Test model output channel and spatial shape validation.

    Arguments:
        output_shape: model output dimensions
        error: expected error message
    """
    processor = _processor(_OutputModel(output_shape))

    with pytest.raises(ValueError, match=error):
        processor.upscale(np.zeros((2, 2, 3), dtype=np.uint8))


def test_rejects_invalid_input_channels():
    """Test direct upscale rejects non-RGB arrays."""
    processor = _processor(_IdentityModel())

    with pytest.raises(ValueError, match="HWC RGB"):
        processor.upscale(np.zeros((2, 2, 4), dtype=np.uint8))
