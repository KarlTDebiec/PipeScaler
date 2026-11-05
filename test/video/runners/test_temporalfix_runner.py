#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Portable TemporalFix configuration, metadata, process, and validation checks."""

from __future__ import annotations

import json
from os import name as os_name
from pathlib import Path
from subprocess import TimeoutExpired
from types import SimpleNamespace
from typing import Any, Never
from venv import EnvBuilder

import pytest

from pipescaler.core import PipeScalerError
from pipescaler.video.core.temporalfix_runtime import (
    import_temporal_runtime,
    inspect_temporal_input,
    temporal_windows,
)
from pipescaler.video.core.temporalfix_settings import TemporalFixSettings
from pipescaler.video.core.video_input import VideoInput
from pipescaler.video.runners import TemporalFixRunner


@pytest.mark.parametrize(
    ("count", "selected", "cuts", "expected"),
    [
        (12, (0, 3), (), [(0, 3, 0, 6)]),
        (12, (3, 6), (), [(3, 6, 0, 9)]),
        (12, (9, 12), (), [(9, 12, 6, 12)]),
        (12, (5, 9), (7,), [(5, 7, 2, 7), (7, 9, 7, 12)]),
        (5, (0, 5), (2,), [(0, 2, 0, 2), (2, 5, 2, 5)]),
    ],
)
def test_temporal_context(
    count: int,
    selected: tuple[int, int],
    cuts: tuple[int, ...],
    expected: list[tuple[int, int, int, int]],
):
    """Preserve true clip and scene edges while supplying radius-three context.

    Arguments:
        count: source frame count
        selected: requested source range
        cuts: first frame indices of new scenes
        expected: output and context intervals
    """
    assert temporal_windows(count, selected, cuts) == expected


@pytest.mark.parametrize(
    "options",
    [
        {"strength": -1},
        {"strength": float("nan")},
        {"strength": 3.1},
        {"tiles": 0},
        {"tiles": 3},
        {"gpu_id": -1},
        {"backend": "mps", "gpu_id": 1},
        {"num_streams": 0},
        {"backend": "unknown"},
        {"matrix": "guess"},
        {"color_range": "auto"},
        {"frame_rate": "0/1"},
        {"frame_range": (4, 3)},
        {"exclude_ranges": ((-1, 2),)},
        {"scene_boundaries": (5, 3)},
        {"scene_boundaries": (3, 3)},
    ],
)
def test_invalid_settings(options: dict[str, Any]):
    """Reject ambiguous color, timing, and unavailable processing settings early.

    Arguments:
        options: invalid configuration overrides
    """
    settings: dict[str, Any] = {"matrix": "709", "color_range": "full"}
    settings.update(options)
    with pytest.raises(ValueError):
        TemporalFixSettings(**settings)


def test_effective_settings_and_repr(tmp_path: Path):
    """Retain exact timing, upstream strength rounding, and reconstructible settings.

    Arguments:
        tmp_path: temporary source directory
    """
    settings = TemporalFixSettings(
        matrix="709",
        color_range="full",
        strength=1.237,
        frame_rate="48000/2002",
        frame_range=(1, 9),
        exclude_ranges=((4, 6),),
        scene_boundaries=(7,),
    )
    assert settings.frame_rate == "24000/1001"
    assert settings.strength == 1.24
    runner = TemporalFixRunner(settings)
    recreated = eval(repr(runner))
    assert recreated.settings == settings
    path = tmp_path / "source 'with spaces'.mkv"
    path.touch()
    output = tmp_path / "output.mkv"
    command = runner.get_command(path, output)
    assert command[command.index("--input") + 1] == str(path.resolve())
    assert command[command.index("--output") + 1] == str(output)


@pytest.mark.parametrize("backend", ["cpu", "mps"])
def test_case_insensitive_settings_are_canonical(backend: str):
    """Give case variants the same worker backend and checkpoint configuration.

    Arguments:
        backend: execution backend to normalize
    """
    assert TemporalFixSettings(
        matrix="2020NCL", color_range="FULL", backend=backend.upper()
    ) == TemporalFixSettings(matrix="2020ncl", color_range="full", backend=backend)


@pytest.mark.parametrize(
    ("available", "fallback", "message"),
    [(False, "0", "MPS is unavailable"), (True, "1", "fallback must be disabled")],
)
def test_mps_runtime_requirements(
    monkeypatch: pytest.MonkeyPatch, available: bool, fallback: str, message: str
):
    """Reject unavailable MPS and CPU operator fallback.

    Arguments:
        monkeypatch: fixture for replacing optional runtime discovery
        available: whether the worker exposes MPS
        fallback: requested CPU fallback setting
        message: expected error
    """
    module = "pipescaler.video.core.temporalfix_runtime"
    modules = {
        "vapoursynth": SimpleNamespace(__version__=SimpleNamespace(release_major=82)),
        "vs_temporalfix": SimpleNamespace(),
        "torch": SimpleNamespace(
            backends=SimpleNamespace(
                mps=SimpleNamespace(is_available=lambda: available)
            )
        ),
    }
    monkeypatch.setattr(f"{module}.import_module", modules.__getitem__)
    monkeypatch.setattr(f"{module}.version", lambda _name: "2.4.1")
    monkeypatch.setenv("PYTORCH_ENABLE_MPS_FALLBACK", fallback)
    with pytest.raises(RuntimeError, match=message):
        import_temporal_runtime("mps")


def test_worker_preserves_virtual_environment(tmp_path: Path):
    """Use the selected virtual environment rather than its base interpreter.

    Arguments:
        tmp_path: temporary worker directory
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
    prefix = runner._execute(
        [str(runner.worker_python_path), "-c", "import sys; print(sys.prefix)"]
    ).strip()
    assert Path(prefix).resolve() == worker_dir_path.resolve()


@pytest.mark.parametrize(
    "response", [[], None, {}, {"width": True, "height": 2, "frames": 8}]
)
def test_malformed_worker_metadata_is_a_domain_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, response: object
):
    """Reject invalid worker responses before pipeline code can use their fields.

    Arguments:
        tmp_path: temporary input path
        monkeypatch: fixture for supplying an invalid worker response
        response: malformed inspection response
    """
    path = tmp_path / "input.mkv"
    path.touch()
    runner = TemporalFixRunner(TemporalFixSettings(matrix="709", color_range="full"))
    monkeypatch.setattr(
        runner,
        "_execute",
        lambda command: "3.14" if "-c" in command else json.dumps(response),
    )
    with pytest.raises(PipeScalerError, match="metadata"):
        runner.inspect(path)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("frame_rate", "1/0"),
        ("frame_rate", "0/1"),
        ("models", []),
        ("versions", {}),
        ("frames", None),
    ],
)
def test_invalid_worker_metadata_fields(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, field: str, value: object
):
    """Check field values rather than only accepting a top-level JSON object.

    Arguments:
        tmp_path: temporary input path
        monkeypatch: fixture for replacing the worker response
        field: metadata field to invalidate
        value: invalid replacement value
    """
    path = tmp_path / "input.mkv"
    path.touch()
    response: dict[str, Any] = {
        "width": 2,
        "height": 2,
        "frames": 8,
        "frame_rate": "24000/1001",
        "models": {"weights": "fingerprint"},
        "versions": {"runtime": "version"},
    }
    response[field] = value
    runner = TemporalFixRunner(TemporalFixSettings(matrix="709", color_range="full"))
    monkeypatch.setattr(
        runner,
        "_execute",
        lambda command: "3.14" if "-c" in command else json.dumps(response),
    )
    with pytest.raises(PipeScalerError, match="metadata"):
        runner.inspect(path)


@pytest.mark.parametrize("plugin_name", ["bs", "akarin", "vszip"])
def test_native_plugin_changes_invalidate_runtime_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, plugin_name: str
):
    """Include actual loaded decoder/filter binaries even if versions stay unchanged.

    Arguments:
        tmp_path: temporary fake native-plugin and model files
        monkeypatch: fixture for replacing only optional native runtime boundaries
        plugin_name: decoder or filter plugin whose binary changes
    """
    package_path = tmp_path / "vs_temporalfix"
    model_path = package_path / "models"
    model_path.mkdir(parents=True)
    (model_path / "temporalfix_s2_v1.pth").write_bytes(b"fixed model")
    source_path = tmp_path / "input.mkv"
    source_path.touch()
    plugin_path = tmp_path / "native-plugin.dll"
    plugin_path.write_bytes(b"native plugin one")
    plugin = SimpleNamespace(version="1", plugin_path=str(plugin_path))
    vs = SimpleNamespace(
        core=SimpleNamespace(**{plugin_name: plugin}), __version__="R82"
    )
    upstream = SimpleNamespace(__file__=str(package_path / "__init__.py"))
    module = "pipescaler.video.core.temporalfix_runtime"
    monkeypatch.setattr(
        f"{module}.import_temporal_runtime", lambda _backend: (vs, upstream)
    )
    monkeypatch.setattr(
        f"{module}._open_clip",
        lambda *_args: SimpleNamespace(
            num_frames=8, width=2, height=2, fps_num=24, fps_den=1
        ),
    )
    monkeypatch.setattr(f"{module}.version", lambda _name: "test-version")
    settings = TemporalFixSettings(matrix="709", color_range="full")
    before = inspect_temporal_input(VideoInput(source_path), settings)
    plugin_path.write_bytes(b"native plugin two")
    after = inspect_temporal_input(VideoInput(source_path), settings)
    assert before["models"] == after["models"]
    assert before["versions"] != after["versions"]


def test_output_metadata_validation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Reject incomplete output or altered timing even when a worker exits cleanly.

    Arguments:
        tmp_path: temporary output directory
        monkeypatch: fixture for replacing ffprobe execution
    """
    runner = TemporalFixRunner(TemporalFixSettings(matrix="709", color_range="full"))
    monkeypatch.setattr(
        "pipescaler.video.runners.temporalfix_runner.val_executable",
        lambda *_args: Path("ffprobe"),
    )
    metadata = {"width": 32, "height": 32, "frame_rate": "24000/1001"}
    stream = {
        "width": 32,
        "height": 32,
        "avg_frame_rate": "24000/1001",
        "nb_read_frames": "4",
        "time_base": "1/1000",
        "codec_name": "ffv1",
        "pix_fmt": "gbrp16le",
        "color_range": "pc",
    }
    monkeypatch.setattr(
        "pipescaler.video.runners.temporalfix_runner.run_command",
        lambda *_args, **_kwargs: (
            0,
            json.dumps(
                {
                    "streams": [stream],
                    "frames": [
                        {"best_effort_timestamp": stamp} for stamp in (0, 42, 83, 125)
                    ],
                }
            ),
            "",
        ),
    )
    runner.validate_output(tmp_path / "out.mkv", metadata, 4)
    for field, value in [
        ("nb_read_frames", "3"),
        ("width", 16),
        ("avg_frame_rate", "24/1"),
    ]:
        original = stream[field]
        stream[field] = value
        with pytest.raises(PipeScalerError, match="validation"):
            runner.validate_output(tmp_path / "out.mkv", metadata, 4)
        stream[field] = original


@pytest.mark.parametrize(
    "failure",
    [
        PipeScalerError("worker interrupted"),
        TimeoutExpired("worker", 1),
        KeyboardInterrupt(),
    ],
)
def test_worker_failure_preserves_destination(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: BaseException
):
    """Keep the previous destination when the worker fails after writing partial data.

    Arguments:
        tmp_path: temporary input and output files
        monkeypatch: fixture for replacing only subprocess execution
        failure: worker interruption or timeout to simulate
    """
    source_path = tmp_path / "source.mkv"
    source_path.touch()
    destination = tmp_path / "output.mkv"
    destination.write_bytes(b"previous valid destination")
    runner = TemporalFixRunner(TemporalFixSettings(matrix="709", color_range="full"))
    monkeypatch.setattr(
        "pipescaler.video.runners.temporalfix_runner.val_executable",
        lambda *_args: Path("ffmpeg"),
    )

    def fail(command: list[str]) -> Never:
        """Write a partial worker output and simulate process failure.

        Arguments:
            command: actual literal worker command
        Raises:
            BaseException: always, simulating timeout or cancellation cleanup
        """
        Path(command[command.index("--output") + 1]).write_bytes(b"partial")
        raise failure

    monkeypatch.setattr(runner, "_execute", fail)
    with pytest.raises(type(failure)):
        runner.render_range(VideoInput(source_path), destination, {"frames": 4}, (0, 4))
    assert destination.read_bytes() == b"previous valid destination"
    assert not list(tmp_path.glob(".temporalfix-*"))


@pytest.mark.parametrize(
    ("frames", "width", "height"), [(3, 32, 32), (8, 31, 32), (8, 32, 31)]
)
def test_short_or_odd_input_is_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    frames: int,
    width: int,
    height: int,
):
    """Enforce upstream minimum length and even geometry without native plugins.

    Arguments:
        tmp_path: temporary source path
        monkeypatch: fixture for replacing runtime import and decoded metadata
        frames: simulated source frame count
        width: simulated source width
        height: simulated source height
    """
    source_path = tmp_path / "input.mkv"
    source_path.touch()
    module = "pipescaler.video.core.temporalfix_runtime"
    monkeypatch.setattr(
        f"{module}.import_temporal_runtime", lambda _backend: (None, None)
    )
    monkeypatch.setattr(
        f"{module}._open_clip",
        lambda *_args: SimpleNamespace(num_frames=frames, width=width, height=height),
    )
    with pytest.raises(ValueError, match="at least four frames and even dimensions"):
        inspect_temporal_input(
            VideoInput(source_path),
            TemporalFixSettings(matrix="709", color_range="full"),
        )
