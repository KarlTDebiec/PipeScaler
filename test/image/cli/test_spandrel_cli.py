#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Spandrel execution settings through the image CLI."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, Mock

import numpy as np
import pytest
import torch
from PIL import Image
from spandrel import ImageModelDescriptor

from pipescaler.image.cli import ImageProcessorsCli
from pipescaler.image.cli.processors import SpandrelCli


@pytest.fixture
def image_paths(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Create a source image, empty mock checkpoint, and output path.

    Arguments:
        tmp_path: temporary directory
    Returns:
        source image, model checkpoint, and output image paths
    """
    input_path = tmp_path / "input.png"
    model_path = tmp_path / "model.safetensors"
    output_path = tmp_path / "output.png"
    Image.new("RGB", (2, 3), (19, 83, 211)).save(input_path)
    model_path.touch()
    return input_path, model_path, output_path


def test_execution_controls_reach_model(
    image_paths: tuple[Path, Path, Path], monkeypatch: pytest.MonkeyPatch
):
    """Execute the registered CLI with relative paths and BF16 precision.

    Arguments:
        image_paths: temporary source, checkpoint, and output paths
        monkeypatch: fixture for replacing model loading
    """
    input_path, model_path, output_path = image_paths
    monkeypatch.chdir(input_path.parent)
    descriptor = MagicMock(spec=ImageModelDescriptor)
    descriptor.input_channels = descriptor.output_channels = 3
    descriptor.supports_bfloat16 = True
    descriptor.to.return_value = descriptor
    descriptor.eval.return_value = descriptor
    descriptor.side_effect = lambda tensor: tensor
    loader = Mock(return_value=descriptor)
    monkeypatch.setattr(
        "pipescaler.image.operators.processors.spandrel_processor.ModelLoader.load_from_file",
        loader,
    )
    ImageProcessorsCli.main(
        [
            "spandrel",
            "--model-input-path",
            model_path.name,
            "--device",
            "cpu",
            "--precision",
            "bfloat16",
            input_path.name,
            output_path.name,
        ]
    )

    loader.assert_called_once_with(model_path.resolve())
    descriptor.to.assert_called_once_with(
        device=torch.device("cpu"), dtype=torch.bfloat16
    )
    assert descriptor.call_args.args[0].dtype == torch.bfloat16
    with Image.open(output_path) as output:
        np.testing.assert_array_equal(
            np.asarray(output), np.full((3, 2, 3), [19, 83, 211])
        )


def test_execution_defaults(image_paths: tuple[Path, Path, Path]):
    """Keep automatic device selection and FP32 as the CLI defaults.

    Arguments:
        image_paths: temporary source, checkpoint, and output paths
    """
    input_path, model_path, output_path = image_paths
    args = SpandrelCli.argparser().parse_args(
        ["--model-input-path", str(model_path), str(input_path), str(output_path)]
    )
    assert args.device == "auto"
    assert args.precision == "float32"


def test_invalid_precision_is_an_argument_error(
    image_paths: tuple[Path, Path, Path], capsys: pytest.CaptureFixture[str]
):
    """Reject unsupported precision names before model loading or output writing.

    Arguments:
        image_paths: temporary source, checkpoint, and output paths
        capsys: captured CLI output
    """
    input_path, model_path, output_path = image_paths
    with pytest.raises(SystemExit) as exc:
        SpandrelCli.main(
            [
                "--model-input-path",
                str(model_path),
                "--precision",
                "int8",
                str(input_path),
                str(output_path),
            ]
        )
    assert exc.value.code == 2
    assert "argument --precision:" in capsys.readouterr().err
    assert not output_path.exists()


def test_unavailable_device_preserves_output(
    image_paths: tuple[Path, Path, Path], monkeypatch: pytest.MonkeyPatch
):
    """Fail an unavailable CUDA request without creating an output image.

    Arguments:
        image_paths: temporary source, checkpoint, and output paths
        monkeypatch: fixture for replacing CUDA availability
    """
    input_path, model_path, output_path = image_paths
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)
    with pytest.raises(ValueError, match="CUDA is unavailable"):
        SpandrelCli.main(
            [
                "--model-input-path",
                str(model_path),
                "--device",
                "cuda:0",
                str(input_path),
                str(output_path),
            ]
        )
    assert not output_path.exists()
