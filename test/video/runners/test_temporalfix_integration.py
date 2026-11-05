#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Opt-in real TemporalFix worker checks with generated 16-bit source frames.

Set PIPESCALER_TEMPORALFIX_PYTHON to a provisioned worker interpreter. FFmpeg and
ffprobe must be on PATH; normal tests never install native plugins or download models.
"""

from __future__ import annotations

from os import getenv
from pathlib import Path
from subprocess import run
from typing import Any

import cv2
import numpy as np
import pytest
import torch

from pipescaler.common.validation import val_executable
from pipescaler.core.dependencies.temporalfix import import_vs_temporalfix_arch
from pipescaler.pipelines import CheckpointManager
from pipescaler.video.core.pipelines import PipeVideo
from pipescaler.video.core.temporalfix_runtime import build_temporal_clip
from pipescaler.video.core.temporalfix_settings import TemporalFixSettings
from pipescaler.video.core.video_input import VideoInput
from pipescaler.video.pipelines.segments import CheckpointedVideoRunnerSegment
from pipescaler.video.runners import TemporalFixRunner
from test.scripts.generate_temporalfix_sample import (
    generate_temporalfix_sample,
    generate_temporalfix_yuv_video,
)


@pytest.mark.serial
@pytest.mark.parametrize("backend", ["cpu", "mps"])
def test_real_temporalfix_worker(tmp_path: Path, backend: str):
    """Preserve ordering, RGB, timing, exclusions, scene edges, and chunk equivalence.

    Lossless 16-bit output may differ by at most two code values when comparing
    whole and chunked CPU inference. Short scenes deliberately pass through.

    Arguments:
        tmp_path: temporary generated assets and worker output directory
        backend: explicitly selected CPU or Apple MPS execution backend
    """
    python_path = getenv("PIPESCALER_TEMPORALFIX_PYTHON")
    if python_path is None:
        pytest.skip("Provision the optional TemporalFix worker interpreter")
    if backend == "mps" and not torch.backends.mps.is_available():
        pytest.skip("MPS hardware is unavailable")
    if backend == "mps":
        assert getenv("PYTORCH_ENABLE_MPS_FALLBACK") != "1", (
            "Start native MPS tests with PYTORCH_ENABLE_MPS_FALLBACK=0"
        )
    template = generate_temporalfix_sample(tmp_path / "frames")
    runner = TemporalFixRunner(
        TemporalFixSettings(
            matrix="709",
            color_range="full",
            frame_rate="24000/1001",
            scene_boundaries=(7, 10),
            exclude_ranges=((4, 6),),
            backend=backend,
        ),
        worker_python_path=python_path,
    )
    whole_path = tmp_path / "whole.mkv"
    runner.run(template, whole_path)
    manager = CheckpointManager(tmp_path / "checkpoints")
    segment = CheckpointedVideoRunnerSegment(runner, manager, chunk_frames=3)
    source = PipeVideo(path=template)
    output = segment(source)[0]
    assert output.path is not None
    whole = decode_rgb_float(whole_path, 32, 32)
    chunked = decode_rgb_float(output.path, 32, 32)
    assert whole.shape == chunked.shape == (12, 32, 32, 3)
    original_first = cv2.imread(
        str(template.parent / "frame_0000.png"), cv2.IMREAD_UNCHANGED
    )
    assert original_first is not None
    assert np.max(np.abs(whole[0] - original_first[:, :, ::-1] / 65535)) > 0.001
    np.testing.assert_allclose(chunked, whole, atol=2 / 65535, rtol=0)
    for index in (4, 5, 10, 11):
        original = cv2.imread(
            str(template.parent / f"frame_{index:04d}.png"), cv2.IMREAD_UNCHANGED
        )
        assert original is not None
        np.testing.assert_allclose(
            whole[index], original[:, :, ::-1] / 65535, atol=2 / 65535, rtol=0
        )
    assert whole[0, 0, 0, 2] > whole[0, 0, 0, 1] > whole[0, 0, 0, 0]
    assert whole[-1, 0, 0, 0] > whole[-1, 0, 0, 1] > whole[-1, 0, 0, 2]
    assert not np.allclose(whole * 255, np.rint(whole * 255), atol=1e-3)
    previous_mtime = output.path.stat().st_mtime_ns
    assert segment(source)[0].path == output.path
    assert output.path.stat().st_mtime_ns == previous_mtime
    assert output.parents == [source]
    # File input retains native rational timing and selects the requested frame range
    selected_path = tmp_path / "selected.mkv"
    TemporalFixRunner(
        TemporalFixSettings(
            matrix="709",
            color_range="full",
            backend=backend,
            strength=0,
            frame_range=(2, 9),
        ),
        worker_python_path=python_path,
    ).run(whole_path, selected_path)
    selected = decode_rgb_float(selected_path, 32, 32)
    np.testing.assert_allclose(selected, whole[2:9], atol=2 / 65535, rtol=0)
    yuv_path = tmp_path / "limited-yuv.mkv"
    generate_temporalfix_yuv_video(template, yuv_path)
    converted_path = tmp_path / "converted-rgb.mkv"
    TemporalFixRunner(
        TemporalFixSettings(
            matrix="709", color_range="limited", backend=backend, strength=0
        ),
        worker_python_path=python_path,
    ).run(yuv_path, converted_path)
    converted = decode_rgb_float(converted_path, 32, 32)
    assert converted.shape == (12, 32, 32, 3)
    np.testing.assert_allclose(
        converted[0, 0, 0], [0.123456, 0.345678, 0.789012], atol=0.003
    )


def decode_rgb_float(path: Path, width: int, height: int) -> np.ndarray:
    """Decode lossless RGB without reducing to OpenCV's default 8-bit capture.

    Arguments:
        path: completed rendered checkpoint
        width: expected width
        height: expected height
    Returns:
        float32 frames in playback order and RGB channel order
    """
    result = run(
        [
            str(val_executable("ffmpeg")),
            "-v",
            "error",
            "-i",
            str(path),
            "-f",
            "rawvideo",
            "-pix_fmt",
            "gbrp16le",
            "pipe:1",
        ],
        capture_output=True,
        check=True,
    )
    gbr = np.frombuffer(result.stdout, dtype="<u2").reshape((-1, 3, height, width))
    return gbr[:, [2, 0, 1]].transpose(0, 2, 3, 1).astype(np.float32) / 65535


@pytest.mark.serial
@pytest.mark.parametrize(("strength", "tiles"), [(2.0, 1), (1.5, 2)])
def test_native_mps_matches_cpu(tmp_path: Path, strength: float, tiles: int):
    """Verify real MPS dispatch and agreement with CPU inference.

    Arguments:
        tmp_path: generated source directory
        strength: integer or interpolated model strength
        tiles: spatial tile count
    """
    if getenv("PIPESCALER_TEMPORALFIX_PYTHON") is None:
        pytest.skip("Provision the optional TemporalFix worker interpreter")
    if not torch.backends.mps.is_available():
        pytest.skip("MPS hardware is unavailable")
    assert getenv("PYTORCH_ENABLE_MPS_FALLBACK") != "1", (
        "Start native MPS tests with PYTORCH_ENABLE_MPS_FALLBACK=0"
    )
    pytest.importorskip("vapoursynth")
    architecture = import_vs_temporalfix_arch()
    template = generate_temporalfix_sample(tmp_path / "source")
    outputs = {}
    devices = []

    def record_devices(model: Any, arguments: tuple[Any, ...]):
        """Record the architecture's weight and input devices.

        Arguments:
            model: module about to run
            arguments: its positional inputs
        """
        if isinstance(model, architecture.temporalfix_arch):
            devices.append(
                (next(model.parameters()).device.type, arguments[0].device.type)
            )

    with torch.nn.modules.module.register_module_forward_pre_hook(record_devices):
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
            outputs[backend] = np.stack(
                [
                    np.stack([np.asarray(frame[p]) for p in range(3)], axis=2)
                    for frame in clip.frames()
                ]
            )
    assert set(devices) == {("cpu", "cpu"), ("mps", "mps")}
    assert outputs["mps"].shape == (12, 32, 32, 3)
    assert np.isfinite(outputs["mps"]).all()
    np.testing.assert_allclose(outputs["mps"], outputs["cpu"], atol=4 / 65535, rtol=0)
