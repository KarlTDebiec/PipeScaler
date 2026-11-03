#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for SpandrelProcessor."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast
from unittest.mock import MagicMock

import numpy as np
import pytest
import torch
from PIL import Image
from spandrel import Architecture, ImageModelDescriptor

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


def _mock_descriptor(input_channels: int = 3, output_channels: int = 3) -> MagicMock:
    """Create descriptor metadata without allocating model weights.

    Arguments:
        input_channels: declared model input channel count
        output_channels: declared model output channel count
    Returns:
        mock RGB image descriptor with supported precision flags
    """
    descriptor = MagicMock(spec=ImageModelDescriptor)
    descriptor.input_channels = input_channels
    descriptor.output_channels = output_channels
    descriptor.supports_half = True
    descriptor.supports_bfloat16 = True
    descriptor.architecture = MagicMock(spec=Architecture)
    descriptor.architecture.id = "test"
    descriptor.to.return_value = descriptor
    descriptor.eval.return_value = descriptor
    return descriptor


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
    processor.tile_size = processor.target_scale = processor.target_size = None
    processor.device = torch.device("cpu")
    processor.dtype = torch.float32
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
@pytest.mark.parametrize("array_input", [False, True])
def test_spandrel_rejects_invalid_model_output(
    output_shape: tuple[int, int, int, int], error: str, array_input: bool
):
    """Test model output channel and spatial shape validation.

    Arguments:
        output_shape: model output dimensions
        error: expected error message
        array_input: whether to call the array interface directly
    """
    processor = SpandrelProcessor.__new__(SpandrelProcessor)
    processor.tile_size = processor.target_scale = processor.target_size = None
    processor.device = torch.device("cpu")
    processor.dtype = torch.float32
    processor.model = cast(Any, _OutputModel(output_shape))

    input_arr = np.zeros((2, 2, 3), dtype=np.uint8)
    with pytest.raises(ValueError, match=error):
        if array_input:
            processor.upscale(input_arr)
        else:
            processor(Image.fromarray(input_arr))


def test_spandrel_rejects_invalid_input_channels():
    """Test direct upscale rejects non-RGB arrays."""
    processor = SpandrelProcessor.__new__(SpandrelProcessor)
    processor.tile_size = processor.target_scale = processor.target_size = None
    processor.device = torch.device("cpu")
    processor.dtype = torch.float32
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
        lambda *_args, **_kwargs: _mock_descriptor(input_channels, output_channels),
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
        lambda *_args, **_kwargs: _mock_descriptor(),
    )

    with get_temp_file_path(".pth") as model_path:
        model_path.touch()
        processor = SpandrelProcessor(
            model_input_path=model_path, device="cpu", precision="bfloat16"
        )
        recreated = eval(
            repr(processor),
            {
                "Path": __import__("pathlib").Path,
                "SpandrelProcessor": SpandrelProcessor,
            },
        )
        assert recreated.model_input_path == processor.model_input_path
        assert recreated.device == processor.device
        assert recreated.precision == processor.precision


@pytest.mark.parametrize("mode", ["1", "L", "RGB"])
def test_spandrel_restores_input_mode(mode: str):
    """Preserve supported input modes through the shared array conversion.

    Arguments:
        mode: supported input image mode
    """
    processor = SpandrelProcessor.__new__(SpandrelProcessor)
    processor.tile_size = processor.target_scale = processor.target_size = None
    processor.device = torch.device("cpu")
    processor.dtype = torch.float32
    processor.model = cast(Any, _IdentityModel())
    input_image = Image.new(mode, (2, 3), 0)

    output_image = processor(input_image)

    assert output_image.mode == mode
    assert output_image.size == input_image.size
    assert output_image.tobytes() == input_image.tobytes()


@pytest.fixture
def loaded_model(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> tuple[Path, MagicMock]:
    """Supply a mock model checkpoint and deterministic CPU availability.

    Arguments:
        monkeypatch: fixture for replacing model loading and device discovery
        tmp_path: temporary checkpoint directory
    Returns:
        model path and loaded image descriptor
    """
    model_path = tmp_path / "model.pth"
    model_path.touch()
    descriptor = _mock_descriptor()
    monkeypatch.setattr(
        "pipescaler.image.operators.processors.spandrel_processor.ModelLoader.load_from_file",
        lambda *_args, **_kwargs: descriptor,
    )
    monkeypatch.setattr(torch.backends.mps, "is_available", lambda: False)
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)
    return model_path, descriptor


@pytest.mark.parametrize("precision", ["float32", "float16", "bfloat16"])
def test_model_weights_and_input_share_precision(
    loaded_model: tuple[Path, MagicMock], precision: str
):
    """Execute a real tiny model with weights matching the selected input dtype.

    Arguments:
        loaded_model: temporary checkpoint and mocked loader
        precision: requested floating-point precision
    """
    model_path, descriptor = loaded_model
    module = torch.nn.Conv2d(3, 3, kernel_size=1, bias=False)
    real_descriptor = ImageModelDescriptor(
        model=module,
        state_dict=module.state_dict(),
        architecture=cast(Architecture, descriptor.architecture),
        purpose="Restoration",
        tags=[],
        supports_half=True,
        supports_bfloat16=True,
        scale=1,
        input_channels=3,
        output_channels=3,
    )
    descriptor.to.side_effect = real_descriptor.to
    processor = SpandrelProcessor(model_path, device="cpu", precision=precision)
    output = processor.upscale_float(np.full((2, 3, 3), 0.123456, dtype=np.float64))

    assert next(module.parameters()).dtype == processor.dtype
    assert output.shape == (2, 3, 3)
    assert output.dtype == np.float32
    assert np.isfinite(output).all()


@pytest.mark.parametrize(
    ("mps_available", "cuda_available", "expected"),
    [(False, False, "cpu"), (False, True, "cuda"), (True, True, "mps")],
)
def test_automatic_device_selection(
    loaded_model: tuple[Path, MagicMock],
    monkeypatch: pytest.MonkeyPatch,
    mps_available: bool,
    cuda_available: bool,
    expected: str,
):
    """Select the documented automatic backend and place the model explicitly.

    Arguments:
        loaded_model: temporary checkpoint and mocked loader
        monkeypatch: fixture for replacing device discovery
        mps_available: whether MPS is available
        cuda_available: whether CUDA is available
        expected: selected backend name
    """
    model_path, descriptor = loaded_model
    monkeypatch.setattr(torch.backends.mps, "is_available", lambda: mps_available)
    monkeypatch.setattr(torch.cuda, "is_available", lambda: cuda_available)
    processor = SpandrelProcessor(model_path)

    assert str(processor.device) == expected
    descriptor.to.assert_called_once_with(
        device=torch.device(expected), dtype=torch.float32
    )


@pytest.mark.parametrize("device", ["cuda", "cuda:0", "mps"])
def test_explicit_unavailable_device_does_not_fall_back(
    loaded_model: tuple[Path, MagicMock], device: str
):
    """Reject unavailable requests before attempting model placement.

    Arguments:
        loaded_model: temporary checkpoint and mocked loader
        device: unavailable requested backend
    """
    model_path, descriptor = loaded_model
    with pytest.raises(ValueError, match="unavailable"):
        SpandrelProcessor(model_path, device=device)
    descriptor.to.assert_not_called()


@pytest.mark.parametrize("device", ["not-a-device", "meta", "cpu:0"])
def test_invalid_device(loaded_model: tuple[Path, MagicMock], device: str):
    """Reject unsupported device syntax, types, and CPU indices.

    Arguments:
        loaded_model: temporary checkpoint and mocked loader
        device: invalid execution device
    """
    model_path, _ = loaded_model
    with pytest.raises(ValueError):
        SpandrelProcessor(model_path, device=device)


def test_cuda_device_index(
    loaded_model: tuple[Path, MagicMock], monkeypatch: pytest.MonkeyPatch
):
    """Accept an available CUDA index and reject out-of-range indices.

    Arguments:
        loaded_model: temporary checkpoint and mocked loader
        monkeypatch: fixture for replacing CUDA discovery
    """
    model_path, descriptor = loaded_model
    monkeypatch.setattr(torch.cuda, "is_available", lambda: True)
    monkeypatch.setattr(torch.cuda, "device_count", lambda: 2)
    processor = SpandrelProcessor(model_path, device="cuda:1")
    assert processor.device == torch.device("cuda:1")
    descriptor.to.assert_called_once_with(
        device=torch.device("cuda:1"), dtype=torch.float32
    )
    with pytest.raises(ValueError, match="index is unavailable"):
        SpandrelProcessor(model_path, device="cuda:2")


@pytest.mark.parametrize(
    ("precision", "flag"),
    [("float16", "supports_half"), ("bfloat16", "supports_bfloat16")],
)
def test_unsupported_precision(
    loaded_model: tuple[Path, MagicMock], precision: str, flag: str
):
    """Honor descriptor precision capabilities before casting weights.

    Arguments:
        loaded_model: temporary checkpoint and mocked loader
        precision: unsupported precision name
        flag: descriptor capability to disable
    """
    model_path, descriptor = loaded_model
    setattr(descriptor, flag, False)
    with pytest.raises(ValueError, match="does not support precision"):
        SpandrelProcessor(model_path, device="cpu", precision=precision)
    descriptor.to.assert_not_called()


def test_placement_error_does_not_fall_back(loaded_model: tuple[Path, MagicMock]):
    """Propagate model placement failures instead of silently changing devices.

    Arguments:
        loaded_model: temporary checkpoint and mocked loader
    """
    model_path, descriptor = loaded_model
    descriptor.to.side_effect = AssertionError("placement failure")
    with pytest.raises(AssertionError, match="placement failure"):
        SpandrelProcessor(model_path, device="cpu")
    assert descriptor.to.call_count == 1


@pytest.mark.parametrize("interface", ["image", "uint8", "float"])
def test_rgb_channels_reach_model_in_rgb_order(
    loaded_model: tuple[Path, MagicMock], interface: str
):
    """Use a red-channel-only model to expose cancelling RGB/BGR swaps.

    Arguments:
        loaded_model: temporary checkpoint and mocked loader
        interface: public inference interface to exercise
    """
    model_path, descriptor = loaded_model
    descriptor.side_effect = lambda tensor: tensor[:, :1].expand(-1, 3, -1, -1)
    processor = SpandrelProcessor(model_path, device="cpu")
    image = np.full((2, 3, 3), [19, 83, 211], dtype=np.uint8)
    if interface == "image":
        output = np.asarray(processor(Image.fromarray(image)))
    elif interface == "uint8":
        output = processor.upscale(image)
    else:
        output = processor.upscale_float(image.astype(np.float32) / 255) * 255
    np.testing.assert_allclose(output, np.full((2, 3, 3), 19), atol=1e-5)


def test_float_input_keeps_fractional_values_and_caller_memory(
    loaded_model: tuple[Path, MagicMock],
):
    """Retain sub-byte detail and isolate read-only strided caller arrays.

    Arguments:
        loaded_model: temporary checkpoint and mocked loader
    """
    model_path, descriptor = loaded_model

    def add_in_place(tensor: torch.Tensor) -> torch.Tensor:
        """Simulate a model that mutates its input before returning it.

        Arguments:
            tensor: model input
        Returns:
            mutated tensor
        """
        return tensor.add_(0.1)

    descriptor.side_effect = add_in_place
    processor = SpandrelProcessor(model_path, device="cpu")
    image = np.full((3, 2, 3), 0.123456, dtype=np.float64)[:, ::-1]
    image.flags.writeable = False
    output = processor.upscale_float(image)
    assert output.dtype == np.float32
    assert output.flags.c_contiguous
    np.testing.assert_allclose(output, 0.223456, atol=1e-7)
    np.testing.assert_array_equal(image, 0.123456)
    assert not np.allclose(output * 255, np.rint(output * 255))


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -0.01, 1.01])
def test_float_input_rejects_invalid_values(
    loaded_model: tuple[Path, MagicMock], value: float
):
    """Reject non-finite and out-of-range normalized inputs.

    Arguments:
        loaded_model: temporary checkpoint and mocked loader
        value: invalid normalized channel value
    """
    model_path, descriptor = loaded_model
    processor = SpandrelProcessor(model_path, device="cpu")
    with pytest.raises(ValueError, match="finite values in"):
        processor.upscale_float(np.full((2, 2, 3), value, dtype=np.float32))
    descriptor.assert_not_called()


@pytest.mark.parametrize("interface", ["uint8", "float"])
def test_array_interfaces_reject_wrong_dtypes(
    loaded_model: tuple[Path, MagicMock], interface: str
):
    """Keep integer and normalized floating-point array contracts unambiguous.

    Arguments:
        loaded_model: temporary checkpoint and mocked loader
        interface: public array interface to exercise
    """
    model_path, _ = loaded_model
    processor = SpandrelProcessor(model_path, device="cpu")
    with pytest.raises(TypeError):
        if interface == "uint8":
            processor.upscale(np.zeros((2, 2, 3), dtype=np.float32))
        else:
            processor.upscale_float(np.zeros((2, 2, 3), dtype=np.uint8))


def test_float_output_rejects_nonfinite_values(loaded_model: tuple[Path, MagicMock]):
    """Report invalid model numerics before image conversion can hide them.

    Arguments:
        loaded_model: temporary checkpoint and mocked loader
    """
    model_path, descriptor = loaded_model
    descriptor.return_value = torch.full((1, 3, 2, 2), float("nan"))
    processor = SpandrelProcessor(model_path, device="cpu")
    with pytest.raises(ValueError, match="finite values"):
        processor.upscale_float(np.zeros((2, 2, 3), dtype=np.float32))
