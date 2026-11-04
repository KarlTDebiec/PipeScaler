#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Check explicit Apple GPU dispatch and agreement with upstream CPU inference."""

from __future__ import annotations

from importlib import import_module
from os import getenv
from os import name as os_name
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from venv import EnvBuilder

import numpy as np
import pytest
import torch

from pipescaler.video.core.temporalfix_mps import import_mps_torch
from pipescaler.video.core.temporalfix_runtime import (
    build_temporal_clip,
)
from pipescaler.video.core.temporalfix_settings import TemporalFixSettings
from pipescaler.video.core.video_input import VideoInput
from pipescaler.video.runners import TemporalFixRunner
from test.scripts.generate_temporalfix_sample import generate_temporalfix_sample


def test_mps_gpu_index_is_validated():
    """Accept the canonical Apple GPU and reject nonexistent device indices."""
    assert (
        TemporalFixSettings(matrix="709", color_range="full", backend="MPS").backend
        == "mps"
    )
    with pytest.raises(ValueError, match="GPU index zero"):
        TemporalFixSettings(matrix="709", color_range="full", backend="mps", gpu_id=1)


@pytest.mark.parametrize(
    ("available", "fallback", "message"),
    [(False, "0", "MPS is unavailable"), (True, "1", "fallback must be disabled")],
)
def test_mps_runtime_rejects_unavailable_or_cpu_fallback(
    monkeypatch: pytest.MonkeyPatch, available: bool, fallback: str, message: str
):
    """Reject missing MPS and fallback settings before any model is constructed.

    Arguments:
        monkeypatch: fixture for replacing only optional runtime discovery
        available: whether the fake worker exposes Apple GPU execution
        fallback: requested PyTorch MPS CPU fallback environment value
        message: expected actionable runtime error
    """
    vs = SimpleNamespace(__version__=SimpleNamespace(release_major=82))
    modules = {
        "vapoursynth": vs,
        "vs_temporalfix": SimpleNamespace(),
        "torch": SimpleNamespace(
            backends=SimpleNamespace(
                mps=SimpleNamespace(is_available=lambda: available)
            )
        ),
    }
    module_name = "pipescaler.video.core.temporalfix_mps"
    monkeypatch.setattr(f"{module_name}.import_module", modules.__getitem__)
    monkeypatch.setenv("PYTORCH_ENABLE_MPS_FALLBACK", fallback)
    with pytest.raises(RuntimeError, match=message):
        import_mps_torch()


@pytest.mark.serial
@pytest.mark.parametrize(("strength", "tiles"), [(2.0, 1), (1.5, 1), (2.0, 2)])
def test_native_mps_matches_cpu_and_uses_gpu(
    tmp_path: Path, strength: float, tiles: int
):
    """Match CPU FP32 with real MPS tensors, interpolation, tiles, cuts, and exclusions.

    The tolerance is four 16-bit codes before final file quantization. Values
    remain floating point, and exclusions and short scenes pass through unchanged.

    Arguments:
        tmp_path: temporary generated source directory
        strength: integer or interpolated checkpoint strength
        tiles: upstream spatial tile count shared by CPU and MPS
    """
    if getenv("PIPESCALER_TEMPORALFIX_PYTHON") is None:
        pytest.skip("Provision the optional TemporalFix worker interpreter")
    if not torch.backends.mps.is_available():
        pytest.skip("MPS hardware is unavailable")
    pytest.importorskip("vapoursynth")
    architecture = import_module("vs_temporalfix.models.temporalfix_arch")
    template = generate_temporalfix_sample(tmp_path / "source")
    outputs = {}
    dispatches = []

    def inspect_dispatch(model: Any, arguments: tuple[Any, ...]):
        """Capture the actual root architecture's weight and input devices.

        Arguments:
            model: module about to execute inference
            arguments: positional inputs supplied to the module
        """
        if isinstance(model, architecture.temporalfix_arch):
            dispatches.append(
                (next(model.parameters()).device.type, arguments[0].device.type)
            )

    with torch.nn.modules.module.register_module_forward_pre_hook(inspect_dispatch):
        for backend in ("cpu", "mps"):
            settings = TemporalFixSettings(
                matrix="709",
                color_range="full",
                backend=backend,
                strength=strength,
                tiles=tiles,
                frame_rate="24000/1001",
                scene_boundaries=(7, 10),
                exclude_ranges=((4, 6),),
            )
            clip = build_temporal_clip(VideoInput(template), settings, (0, 12))
            frames = []
            for number in range(12):
                with clip.get_frame(number) as frame:
                    frames.append(
                        np.stack(
                            [np.asarray(frame[plane]) for plane in range(3)], axis=2
                        )
                    )
            outputs[backend] = np.stack(frames)
    assert ("mps", "mps") in dispatches
    assert ("cpu", "cpu") in dispatches
    assert all(weights == inputs for weights, inputs in dispatches)
    assert outputs["mps"].shape == (12, 32, 32, 3)
    assert np.isfinite(outputs["mps"]).all()
    np.testing.assert_allclose(outputs["mps"], outputs["cpu"], atol=4 / 65535, rtol=0)
    assert not np.allclose(
        outputs["mps"] * 255, np.rint(outputs["mps"] * 255), atol=1e-3
    )


def test_worker_preserves_virtual_environment(tmp_path: Path):
    """Run the requested virtual environment rather than its resolved base Python.

    Arguments:
        tmp_path: temporary interpreter environment directory
    """
    worker_dir_path = tmp_path / "worker"
    EnvBuilder(with_pip=False, symlinks=os_name != "nt").create(worker_dir_path)
    worker_python_path = worker_dir_path / "bin/python"
    if os_name == "nt":
        worker_python_path = worker_dir_path / "Scripts/python.exe"
    runner = TemporalFixRunner(
        TemporalFixSettings(matrix="709", color_range="full"),
        worker_python_path=worker_python_path,
    )
    assert runner.worker_python_path == worker_python_path.absolute()
    prefix = runner._execute(
        [str(runner.worker_python_path), "-c", "import sys; print(sys.prefix)"]
    ).strip()
    assert Path(prefix).resolve() == worker_dir_path.resolve()
