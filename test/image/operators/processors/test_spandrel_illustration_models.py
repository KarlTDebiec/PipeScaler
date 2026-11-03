#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Optional inference checks for externally provisioned IllustrationJaNai V3 weights.

Set `PIPESCALER_ILLUSTRATION_MODEL_DIR` to a directory containing the two released
safetensors checkpoints. `PIPESCALER_ILLUSTRATION_DEVICE` selects a device and
defaults to CPU. No checkpoints are downloaded by these tests.
"""

from __future__ import annotations

from collections.abc import Callable
from os import getenv
from pathlib import Path

import numpy as np
import pytest

from pipescaler.image.operators.processors import SpandrelProcessor


@pytest.mark.serial
@pytest.mark.parametrize("precision", ["float32", "bfloat16"])
@pytest.mark.parametrize(
    ("model_name", "architecture"),
    [
        ("4x_IllustrationJaNai_V3detail_HAT_L_28k_bf16.safetensors", "HAT"),
        ("4x_IllustrationJaNai_V3denoise_DAT2_27k_bf16.safetensors", "DAT"),
    ],
)
def test_released_illustration_checkpoint(
    model_name: str,
    architecture: str,
    precision: str,
    record_property: Callable[[str, object], None],
):
    """Load released weights and preserve their RGB scale and precision metadata.

    Arguments:
        model_name: released safetensors checkpoint filename
        architecture: expected Spandrel architecture identifier
        precision: execution precision to verify
        record_property: fixture for recording metadata in the test report
    """
    model_dir = getenv("PIPESCALER_ILLUSTRATION_MODEL_DIR")
    if model_dir is None:
        pytest.skip(
            "Set PIPESCALER_ILLUSTRATION_MODEL_DIR to provision real checkpoints"
        )
    processor = SpandrelProcessor(
        Path(model_dir) / model_name,
        device=getenv("PIPESCALER_ILLUSTRATION_DEVICE", "cpu"),
        precision=precision,
    )
    record_property("model", model_name)
    record_property("architecture", processor.model.architecture.id)
    record_property("native_scale", processor.model.scale)
    record_property("supports_float16", processor.model.supports_half)
    record_property("supports_bfloat16", processor.model.supports_bfloat16)
    record_property("device", str(processor.device))
    record_property("precision", processor.precision)

    image = (
        np.random.default_rng(0).uniform(0.1, 0.9, size=(16, 16, 3)).astype(np.float32)
    )
    output = processor.upscale_float(image)

    assert processor.model.architecture.id == architecture
    assert processor.model.scale == 4
    assert not processor.model.supports_half
    assert processor.model.supports_bfloat16
    assert output.shape == (64, 64, 3)
    assert output.dtype == np.float32
    assert np.isfinite(output).all()
    assert output.min() >= 0
    assert output.max() <= 1


@pytest.mark.serial
@pytest.mark.parametrize(
    "model_name",
    [
        "4x_IllustrationJaNai_V3detail_HAT_L_28k_bf16.safetensors",
        "4x_IllustrationJaNai_V3denoise_DAT2_27k_bf16.safetensors",
    ],
)
def test_tiled_illustration_checkpoint(
    model_name: str, record_property: Callable[[str, object], None]
):
    """Compare tiled and full-frame transformer inference on a smooth RGB sample.

    Context differences are allowed up to mean absolute error 0.05 and maximum
    error 0.2 in normalized RGB. These are smoke-test bounds, not equivalence or
    perceptual-quality guarantees; projects must compare representative footage.

    Arguments:
        model_name: provisioned release checkpoint
        record_property: fixture for recording measured context differences
    """
    model_dir = getenv("PIPESCALER_ILLUSTRATION_MODEL_DIR")
    if model_dir is None:
        pytest.skip(
            "Provision IllustrationJaNai checkpoints to compare tiled inference"
        )
    processor = SpandrelProcessor(
        Path(model_dir) / model_name,
        device=getenv("PIPESCALER_ILLUSTRATION_DEVICE", "cpu"),
        target_scale=2,
    )
    x, y = np.meshgrid(np.linspace(0.1, 0.9, 23), np.linspace(0.1, 0.9, 21))
    image = np.stack((x, y, (x + y) / 2), axis=2).astype(np.float32)
    full = processor.upscale_float(image)
    processor.tile_size, processor.tile_overlap = 16, 8
    tiled = processor.upscale_float(image)
    error = np.abs(tiled - full)
    record_property("mean_absolute_error", float(error.mean()))
    record_property("maximum_absolute_error", float(error.max()))
    assert tiled.shape == full.shape == (42, 46, 3)
    assert float(error.mean()) < 0.05
    assert float(error.max()) < 0.2
