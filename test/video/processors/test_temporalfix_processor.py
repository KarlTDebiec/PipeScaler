#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Portable TemporalFix configuration, direct invocation, and validation checks."""

from __future__ import annotations

import json
from contextlib import nullcontext
from os import getpid
from pathlib import Path
from threading import get_ident
from types import SimpleNamespace
from typing import Any
from unittest.mock import Mock

import numpy as np
import pytest

from pipescaler.core import PipeScalerError
from pipescaler.core.exceptions import DependencyError
from pipescaler.video.core.temporalfix_runtime import (
    import_temporal_runtime,
    inspect_temporal_input,
    temporal_windows,
)
from pipescaler.video.core.temporalfix_settings import TemporalFixSettings
from pipescaler.video.core.video_input import VideoInput
from pipescaler.video.processors import TemporalFixProcessor


def test_changed_metadata_prevents_rendering(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Reject changed source/runtime fingerprints before graph construction.

    Arguments:
        tmp_path: temporary source file
        monkeypatch: fixture for changing runtime inspection
    """
    source_path = tmp_path / "source.mkv"
    source_path.touch()
    processor = TemporalFixProcessor(
        TemporalFixSettings(matrix="709", color_range="full")
    )
    monkeypatch.setattr(
        processor, "inspect", lambda _source: {"versions": {"model": "new"}}
    )
    build = Mock()
    monkeypatch.setattr(
        "pipescaler.video.processors.temporalfix_processor.build_temporal_clip", build
    )
    with pytest.raises(PipeScalerError, match="changed after inspection"):
        processor.render_range(
            VideoInput(source_path),
            tmp_path / "out.mkv",
            {"versions": {"model": "old"}},
            (0, 4),
        )
    build.assert_not_called()


def test_effective_settings_and_repr():
    """Retain exact timing, upstream rounding, and reconstructible settings."""
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
    processor = TemporalFixProcessor(settings)
    recreated = eval(repr(processor))
    assert recreated.settings == settings


def test_encoder_preserves_planar_order_and_16_bit_samples(
    monkeypatch: pytest.MonkeyPatch,
):
    """Clip and round RGB samples once before streaming 16-bit GBR planes.

    Arguments:
        monkeypatch: fixture for recording encoder input
    """
    planes = [
        np.array([[-0.1, 0, 0.5, 1.1]], dtype=np.float32),
        np.array([[0.1, 0.2, 0.3, 0.4]], dtype=np.float32),
        np.array([[0.123456, 0.345678, 0.789012, 1]], dtype=np.float32),
    ]
    clip = SimpleNamespace(num_frames=1, get_frame=lambda _number: nullcontext(planes))
    process = Mock()
    process.poll.return_value = 0
    process.wait.return_value = 0
    process.stdin.closed = False
    process.stdin.close.side_effect = lambda: setattr(process.stdin, "closed", True)
    start = Mock(return_value=process)
    monkeypatch.setattr(
        "pipescaler.video.processors.temporalfix_processor.Popen", start
    )
    TemporalFixProcessor._encode_clip(clip, ["ffmpeg"])
    actual = b"".join(call.args[0] for call in process.stdin.write.call_args_list)
    expected = np.array(
        [
            [6554, 13107, 19660, 26214],
            [8091, 22654, 51708, 65535],
            [0, 0, 32768, 65535],
        ],
        dtype="<u2",
    )
    np.testing.assert_array_equal(
        np.frombuffer(actual, dtype="<u2").reshape(3, 4), expected
    )
    process.stdin.close.assert_called_once()
    process.kill.assert_not_called()
    process.wait.assert_called()


def test_output_metadata_validation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Reject incomplete output or altered timing after native processing succeeds.

    Arguments:
        tmp_path: temporary output directory
        monkeypatch: fixture for replacing ffprobe execution
    """
    processor = TemporalFixProcessor(
        TemporalFixSettings(matrix="709", color_range="full")
    )
    monkeypatch.setattr(
        "pipescaler.video.processors.temporalfix_processor.val_executable",
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
        "pipescaler.video.processors.temporalfix_processor.run_command",
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
    processor.validate_output(tmp_path / "out.mkv", metadata, 4)
    for field, value in [
        ("nb_read_frames", "3"),
        ("width", 16),
        ("avg_frame_rate", "24/1"),
    ]:
        original = stream[field]
        stream[field] = value
        with pytest.raises(PipeScalerError, match="validation"):
            processor.validate_output(tmp_path / "out.mkv", metadata, 4)
        stream[field] = original


def test_process_rejects_source_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Verify the source snapshot before publishing a standalone selected range.

    Arguments:
        tmp_path: temporary source and destination files
        monkeypatch: fixture for modifying a source during rendering
    """
    source_path = tmp_path / "source.mkv"
    source_path.write_bytes(b"source")
    destination_path = tmp_path / "output.mkv"
    destination_path.write_bytes(b"previous")
    processor = TemporalFixProcessor(
        TemporalFixSettings(matrix="709", color_range="full", frame_range=(1, 5))
    )
    monkeypatch.setattr(processor, "inspect", lambda _source: {"frames": 8})

    def render(
        source: VideoInput,
        output_path: Path,
        _metadata: dict[str, Any],
        frame_range: tuple[int, int],
    ):
        """Change the source after writing a complete scratch video.

        Arguments:
            source: original source specification
            output_path: temporary destination before source verification
            _metadata: inspected source metadata
            frame_range: selected source range
        """
        assert frame_range == (1, 5)
        output_path.write_bytes(b"complete")
        source.input_path.write_bytes(b"changed source")

    monkeypatch.setattr(processor, "render_range", render)
    with pytest.raises(PipeScalerError, match="source changed"):
        processor.process(source_path, destination_path)
    assert destination_path.read_bytes() == b"previous"
    assert not list(tmp_path.glob(".temporalfix-*"))


def test_render_builds_graph_directly_and_publishes_after_validation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Pass scene/range settings directly and preserve the destination until valid.

    Arguments:
        tmp_path: temporary source and destination directory
        monkeypatch: fixture for replacing native graphs and encoding
    """
    source_path = tmp_path / "input.mkv"
    source_path.touch()
    source = VideoInput(source_path)
    settings = TemporalFixSettings(
        matrix="709",
        color_range="full",
        scene_boundaries=(5,),
        exclude_ranges=((2, 4),),
    )
    processor = TemporalFixProcessor(settings)
    metadata = {"frames": 8, "width": 2, "height": 2, "frame_rate": "24000/1001"}
    monkeypatch.setattr(processor, "inspect", lambda _source: metadata)
    clip = SimpleNamespace(width=2, height=2)
    build = Mock(return_value=clip)
    module = "pipescaler.video.processors.temporalfix_processor"
    monkeypatch.setattr(f"{module}.build_temporal_clip", build)
    monkeypatch.setattr(f"{module}.val_executable", Path)
    destination_path = tmp_path / "output 'with spaces'.mkv"
    destination_path.write_bytes(b"previous")

    def encode(actual_clip: Any, command: list[str]):
        """Write an encoded stand-in through the generated FFmpeg command.

        Arguments:
            actual_clip: graph built in the calling process
            command: lossless RGB encoder invocation
        """
        assert actual_clip is clip
        assert command[0] == "ffmpeg"
        assert command[command.index("-framerate") + 1] == "24000/1001"
        assert command[command.index("-pixel_format") + 1] == "gbrp16le"
        assert "-an" in command and "-sn" in command
        Path(command[-1]).write_bytes(b"complete")

    def validate(path: Path, actual_metadata: dict[str, Any], frames: int):
        """Observe validation before atomic destination replacement.

        Arguments:
            path: scratch file beside the destination
            actual_metadata: original source metadata
            frames: selected frame count
        """
        assert destination_path.read_bytes() == b"previous"
        assert path.read_bytes() == b"complete"
        assert actual_metadata is metadata
        assert frames == 5

    monkeypatch.setattr(processor, "_encode_clip", encode)
    monkeypatch.setattr(processor, "validate_output", validate)
    processor.render_range(source, destination_path, metadata, (1, 6))
    build.assert_called_once_with(source, settings, (1, 6))
    assert destination_path.read_bytes() == b"complete"
    assert not list(tmp_path.glob(".temporalfix-*"))


@pytest.mark.parametrize("backend", ["cpu", "mps"])
def test_case_insensitive_settings_are_canonical(backend: str):
    """Give case variants the same processing backend and checkpoint configuration.

    Arguments:
        backend: execution backend to normalize
    """
    assert TemporalFixSettings(
        matrix="2020NCL", color_range="FULL", backend=backend.upper()
    ) == TemporalFixSettings(matrix="2020ncl", color_range="full", backend=backend)


@pytest.mark.parametrize("broken_pipe", [False, True])
def test_encoder_failure_reports_diagnostics(
    monkeypatch: pytest.MonkeyPatch, broken_pipe: bool
):
    """Retain FFmpeg diagnostics and the cause of rejected input.

    Arguments:
        monkeypatch: fixture for replacing FFmpeg startup
        broken_pipe: whether FFmpeg closes its input before all samples are written
    """
    process = Mock()
    process.poll.return_value = 1
    process.wait.return_value = 1
    process.stdin.closed = False
    process.stdin.close.side_effect = lambda: setattr(process.stdin, "closed", True)
    failure = BrokenPipeError("encoder closed")
    if broken_pipe:
        process.stdin.write.side_effect = failure

    def start(_command: list[str], **kwargs: Any) -> Any:
        """Write encoder diagnostics to the supplied temporary log.

        Arguments:
            _command: encoder invocation
            **kwargs: encoder streams
        Returns:
            failing encoder process
        """
        kwargs["stderr"].write(b"encoder diagnostic")
        return process

    monkeypatch.setattr(
        "pipescaler.video.processors.temporalfix_processor.Popen", start
    )
    clip = SimpleNamespace(
        num_frames=1, get_frame=lambda _number: nullcontext([np.zeros((2, 2))] * 3)
    )
    with pytest.raises(PipeScalerError, match="encoder diagnostic") as error:
        TemporalFixProcessor._encode_clip(clip, ["ffmpeg"])
    if broken_pipe:
        assert error.value.__cause__ is failure
    process.wait.assert_called()
    process.stdin.close.assert_called_once()


@pytest.mark.parametrize("failure", [RuntimeError("frame failed"), KeyboardInterrupt()])
def test_frame_failure_reaps_encoder(
    monkeypatch: pytest.MonkeyPatch, failure: BaseException
):
    """Propagate native frame failures while terminating and reaping FFmpeg.

    Arguments:
        monkeypatch: fixture for replacing FFmpeg startup
        failure: exception raised by native frame evaluation
    """
    process = Mock()
    process.poll.return_value = None
    process.stdin.closed = False
    monkeypatch.setattr(
        "pipescaler.video.processors.temporalfix_processor.Popen",
        Mock(return_value=process),
    )
    clip = SimpleNamespace(num_frames=1, get_frame=Mock(side_effect=failure))
    with pytest.raises(type(failure)) as error:
        TemporalFixProcessor._encode_clip(clip, ["ffmpeg"])
    assert error.value is failure
    process.kill.assert_called_once()
    process.wait.assert_called_once()
    process.stdin.close.assert_called_once()


@pytest.mark.parametrize("input_kind", ["path", "str", "source"])
def test_inspect_uses_calling_process(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, input_kind: str
):
    """Inspect directly with the original settings in the caller's process/thread.

    Arguments:
        tmp_path: temporary source directory
        monkeypatch: fixture for replacing native inspection
        input_kind: supported input representation
    """
    source_path = tmp_path / "source 'with spaces'.mkv"
    source_path.touch()
    source = VideoInput(source_path)
    settings = TemporalFixSettings(matrix="709", color_range="full")
    processor = TemporalFixProcessor(settings)
    metadata = {"frames": 8}
    caller = (getpid(), get_ident())

    def inspect(
        actual_source: VideoInput, actual_settings: TemporalFixSettings
    ) -> dict[str, Any]:
        """Record native inspection's arguments and execution context.

        Arguments:
            actual_source: normalized source specification
            actual_settings: processor settings passed directly to the runtime
        Returns:
            source metadata without serialization
        """
        assert actual_source.input_path == source.input_path
        assert actual_settings is settings
        assert (getpid(), get_ident()) == caller
        return metadata

    module = "pipescaler.video.processors.temporalfix_processor"
    monkeypatch.setattr(f"{module}.inspect_temporal_input", inspect)
    monkeypatch.setattr(
        f"{module}.run_command", Mock(side_effect=AssertionError("Unexpected process"))
    )
    inputs = {"path": source_path, "str": str(source_path), "source": source}
    assert processor.inspect(inputs[input_kind]) is metadata


@pytest.mark.parametrize(
    "failure",
    [
        DependencyError("missing runtime"),
        ValueError("invalid source"),
        RuntimeError("native failure"),
        KeyboardInterrupt(),
    ],
)
def test_inspection_failure_propagates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: BaseException
):
    """Preserve the original native inspection exception and Python interruption.

    Arguments:
        tmp_path: temporary source directory
        monkeypatch: fixture for replacing native inspection
        failure: original exception raised by the runtime
    """
    source_path = tmp_path / "input.mkv"
    source_path.touch()
    processor = TemporalFixProcessor(
        TemporalFixSettings(matrix="709", color_range="full")
    )
    monkeypatch.setattr(
        "pipescaler.video.processors.temporalfix_processor.inspect_temporal_input",
        Mock(side_effect=failure),
    )
    with pytest.raises(type(failure)) as error:
        processor.inspect(source_path)
    assert error.value is failure


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


@pytest.mark.parametrize("available", [False, True])
@pytest.mark.parametrize("fallback", ["0", "1"])
def test_mps_runtime_requirements(
    monkeypatch: pytest.MonkeyPatch, available: bool, fallback: str
):
    """Require MPS availability while honoring the user's CPU fallback setting.

    Arguments:
        monkeypatch: fixture for replacing optional runtime discovery
        available: whether the interpreter exposes MPS
        fallback: requested CPU fallback setting
    """
    module = "pipescaler.video.core.temporalfix_runtime"
    vs = SimpleNamespace(__version__=SimpleNamespace(release_major=82))
    temporalfix = SimpleNamespace()
    monkeypatch.setattr(f"{module}.import_vapoursynth", lambda: vs)
    monkeypatch.setattr(f"{module}.import_vs_temporalfix", lambda: temporalfix)
    monkeypatch.setattr(f"{module}.torch.backends.mps.is_available", lambda: available)
    monkeypatch.setattr(f"{module}.version", lambda _name: "2.4.1")
    monkeypatch.setenv("PYTORCH_ENABLE_MPS_FALLBACK", fallback)
    if available:
        assert import_temporal_runtime("mps") == (vs, temporalfix)
    else:
        with pytest.raises(RuntimeError, match="MPS is unavailable"):
            import_temporal_runtime("mps")


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


@pytest.mark.parametrize("stage", ["graph", "encoding", "validation"])
@pytest.mark.parametrize(
    "failure", [RuntimeError("native failure"), KeyboardInterrupt()]
)
def test_render_failure_preserves_destination(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, stage: str, failure: BaseException
):
    """Remove partial output and preserve original errors at each rendering stage.

    Arguments:
        tmp_path: temporary source and destination files
        monkeypatch: fixture for replacing native processing boundaries
        stage: processing stage to interrupt
        failure: original processing exception or Python interruption
    """
    source_path = tmp_path / "source.mkv"
    source_path.touch()
    destination_path = tmp_path / "output.mkv"
    destination_path.write_bytes(b"previous valid destination")
    processor = TemporalFixProcessor(
        TemporalFixSettings(matrix="709", color_range="full")
    )
    metadata = {"frames": 4, "frame_rate": "24/1"}
    monkeypatch.setattr(processor, "inspect", lambda _source: metadata)
    module = "pipescaler.video.processors.temporalfix_processor"
    monkeypatch.setattr(f"{module}.val_executable", Path)
    monkeypatch.setattr(
        f"{module}.build_temporal_clip",
        Mock(return_value=SimpleNamespace(width=2, height=2)),
    )

    def encode(_clip: Any, command: list[str]):
        """Write partial data and optionally propagate an inference failure.

        Arguments:
            _clip: mocked native graph
            command: encoder command naming the scratch output
        Raises:
            BaseException: configured failure during frame evaluation
        """
        Path(command[-1]).write_bytes(b"partial")
        if stage == "encoding":
            raise failure

    monkeypatch.setattr(processor, "_encode_clip", encode)
    monkeypatch.setattr(processor, "validate_output", Mock())
    if stage == "graph":
        monkeypatch.setattr(f"{module}.build_temporal_clip", Mock(side_effect=failure))
    elif stage == "validation":
        monkeypatch.setattr(processor, "validate_output", Mock(side_effect=failure))
    with pytest.raises(type(failure)) as error:
        processor.render_range(
            VideoInput(source_path), destination_path, metadata, (0, 4)
        )
    assert error.value is failure
    assert destination_path.read_bytes() == b"previous valid destination"
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
