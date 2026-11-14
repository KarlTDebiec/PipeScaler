#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Behavioral coverage for streamed native-scale inference and final float resizing."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast
from unittest.mock import MagicMock

import numpy as np
import pytest
import torch
from PIL import Image
from spandrel import Architecture, ImageModelDescriptor, SizeRequirements

from pipescaler.image.core.functions import resize_float
from pipescaler.image.operators.processors import SpandrelProcessor
from pipescaler.image.subdivided_image import SubdividedImage


class PointwiseUpscaler(torch.nn.Module):
    """Apply a color-preserving affine transform and upscale fourfold."""

    def __init__(self):
        """Initialize a tiny model with real weights and a native scale of four."""
        super().__init__()
        self.layer = torch.nn.Conv2d(3, 3, 1)
        self.shapes: list[tuple[int, ...]] = []
        with torch.no_grad():
            self.layer.weight.zero_()
            for channel in range(3):
                self.layer.weight[channel, channel, 0, 0] = 0.75
            assert self.layer.bias is not None
            self.layer.bias.fill_(0.012345)

    def forward(self, tensor: torch.Tensor) -> torch.Tensor:
        """Record padded geometry and upscale transformed input.

        Arguments:
            tensor: BCHW image padded by Spandrel
        Returns:
            native fourfold output
        """
        self.shapes.append(tuple(tensor.shape))
        return torch.nn.functional.interpolate(self.layer(tensor), scale_factor=4)


@pytest.fixture
def checkpoint(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[Path, PointwiseUpscaler]:
    """Provide real descriptor padding and a deterministic color-sensitive model.

    Arguments:
        tmp_path: temporary checkpoint directory
        monkeypatch: fixture for replacing only checkpoint deserialization
    Returns:
        checkpoint path and the module loaded once by the processor
    """
    path = tmp_path / "model.pth"
    path.touch()
    module = PointwiseUpscaler()
    descriptor = ImageModelDescriptor(
        module,
        state_dict=module.state_dict(),
        architecture=cast(Architecture, MagicMock(spec=Architecture)),
        purpose="SR",
        tags=[],
        supports_half=True,
        supports_bfloat16=True,
        scale=4,
        input_channels=3,
        output_channels=3,
        size_requirements=SizeRequirements(minimum=8, multiple_of=8),
    )
    monkeypatch.setattr(
        "pipescaler.image.operators.processors.spandrel_processor.ModelLoader.load_from_file",
        lambda *_args, **_kwargs: descriptor,
    )
    return path, module


@pytest.mark.parametrize("size", [(1, 1), (3, 17), (31, 29), (29, 31)])
@pytest.mark.parametrize("overlap", [0, 1, 5, 11])
def test_tiled_native_output_and_padding(
    checkpoint: tuple[Path, PointwiseUpscaler], size: tuple[int, int], overlap: int
):
    """Preserve every pixel across odd edges, overlaps, and descriptor padding.

    Arguments:
        checkpoint: temporary checkpoint and tiny module
        size: input height and width
        overlap: input tile overlap
    """
    path, module = checkpoint
    image = np.random.default_rng(7).uniform(0.1, 0.9, (*size, 3)).astype(np.float32)
    processor = SpandrelProcessor(
        path, device="cpu", tile_size=12, tile_overlap=overlap
    )
    output = processor.upscale_float(image)
    expected = np.repeat(np.repeat(image * 0.75 + 0.012345, 4, axis=0), 4, axis=1)
    # Dense overlap accumulates many float32 terms; allow a few millionths
    np.testing.assert_allclose(output, expected, atol=3e-6)
    assert output.dtype == np.float32
    assert all(height <= 16 and width <= 16 for _, _, height, width in module.shapes)
    assert all(height % 8 == width % 8 == 0 for _, _, height, width in module.shapes)
    first_count = len(module.shapes)
    processor.upscale_float(image)
    assert len(module.shapes) == first_count * 2
    assert processor.model.model is module


@pytest.mark.parametrize("target", [{"target_scale": 2}, {"target_size": (21, 19)}])
def test_final_resize_preserves_fractional_values(
    checkpoint: tuple[Path, PointwiseUpscaler], target: dict[str, Any]
):
    """Resize native 4x results after float blending and quantize only Pillow output.

    Arguments:
        checkpoint: temporary checkpoint and tiny module
        target: selected final dimensions or scale
    """
    path, _ = checkpoint
    image = np.full((13, 17, 3), [0.123456, 0.234567, 0.345678], dtype=np.float32)
    processor = SpandrelProcessor(
        path, device="cpu", tile_size=12, tile_overlap=3, **target
    )
    output = processor.upscale_float(image)
    size = target.get("target_size", (34, 26))
    assert output.shape == (size[1], size[0], 3)
    np.testing.assert_allclose(
        output, np.broadcast_to(image[0, 0] * 0.75 + 0.012345, output.shape), atol=3e-7
    )
    assert not np.allclose(output * 255, np.rint(output * 255))
    pillow = processor(Image.new("RGB", (17, 13), (19, 83, 211)))
    assert pillow.size == size
    assert pillow.getpixel((0, 0)) == tuple(
        round(value * 0.75 + 0.012345 * 255) for value in (19, 83, 211)
    )


def test_resize_antialiases_without_integer_quantization():
    """Suppress checkerboard aliasing and retain a fractional constant channel."""
    image = np.zeros((16, 16, 3), np.float32)
    image[:, :, 0] = np.indices((16, 16)).sum(axis=0) % 2
    image[:, :, 1] = 0.123456
    output = resize_float(image, (4, 4))
    assert np.max(np.abs(output[:, :, 0] - 0.5)) < 0.01
    np.testing.assert_allclose(output[:, :, 1], 0.123456, atol=1e-7)


@pytest.mark.parametrize(
    "settings",
    [
        {"tile_size": 3},
        {"tile_size": 8, "tile_overlap": 8},
        {"tile_overlap": 1},
        {"tile_overlap": -1},
        {"target_scale": 0},
        {"target_scale": float("nan")},
        {"target_scale": 2, "target_size": (8, 8)},
        {"target_size": (0, 8)},
    ],
)
def test_invalid_geometry(
    checkpoint: tuple[Path, PointwiseUpscaler], settings: dict[str, Any]
):
    """Reject unusable tiling and final output settings before inference.

    Arguments:
        checkpoint: temporary checkpoint and tiny module
        settings: invalid processing configuration
    """
    path, module = checkpoint
    with pytest.raises(ValueError):
        SpandrelProcessor(path, device="cpu", **settings)
    assert not module.shapes


def test_float_reconstruction_rejects_holes_and_wrong_tiles():
    """Reject incomplete coverage and native-scale mismatches explicitly."""
    with pytest.raises(ValueError, match="holes"):
        SubdividedImage.recompose_float(
            [np.ones((2, 2, 3), np.float32)], np.array([[1, 1, 3, 3]]), 4, 0
        )
    with pytest.raises(ValueError, match="dimensions"):
        SubdividedImage.recompose_float(
            [np.ones((1, 2, 3), np.float32)], np.array([[0, 0, 2, 2]]), 4, 0
        )
