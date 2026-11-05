#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Portable restart, invalidation, and atomic-publication checks for video chunks."""

from __future__ import annotations

import json
import shlex
from pathlib import Path
from typing import Any

import pytest

from pipescaler.core import PipeScalerError
from pipescaler.pipelines import CheckpointManager
from pipescaler.video.core.pipelines import PipeVideo
from pipescaler.video.core.temporalfix_settings import TemporalFixSettings
from pipescaler.video.core.video_input import VideoInput
from pipescaler.video.pipelines.segments import CheckpointedVideoProcessorSegment
from pipescaler.video.processors import TemporalFixProcessor


class RecordingProcessor(TemporalFixProcessor):
    """Render tiny JSON stand-ins while preserving real checkpoint orchestration."""

    def __init__(self, *, strength: float = 2):
        """Initialize a processor with a configurable strength.

        Arguments:
            strength: effective setting used to verify cache invalidation
        """
        super().__init__(
            TemporalFixSettings(matrix="709", color_range="full", strength=strength)
        )
        self.calls: list[tuple[int, int]] = []
        """Source ranges rendered during this attempt."""
        self.failure: BaseException | None = None
        """Exception raised on the second chunk, or None."""
        self.change_source = False
        """Whether to mutate source contents during the second chunk."""
        self.model_version = "model-one"
        """Model fingerprint used to verify checkpoint invalidation."""

    def inspect(self, input_path: VideoInput | Path | str) -> dict[str, Any]:
        """Return stable geometry with a configurable model/runtime fingerprint.

        Arguments:
            input_path: existing dummy video source
        Returns:
            synthetic source metadata and selected model identity
        """
        return {
            "width": 2,
            "height": 2,
            "frames": 8,
            "frame_rate": "24000/1001",
            "models": {"checkpoint": self.model_version},
            "versions": {"runtime": "test"},
        }

    def render_range(
        self,
        source: VideoInput,
        output_path: Path,
        metadata: dict[str, Any],
        frame_range: tuple[int, int],
    ):
        """Record the range and simulate configured failures or source changes.

        Arguments:
            source: source whose content may change during processing
            output_path: chunk destination
            metadata: expected source metadata
            frame_range: output frame interval
        Raises:
            BaseException: configured failure on the second chunk
        """
        self.calls.append(frame_range)
        output_path.write_text(json.dumps(list(range(*frame_range))), encoding="utf-8")
        if len(self.calls) == 2:
            if self.change_source:
                source.input_path.write_bytes(b"source changed during processing")
            if self.failure is not None:
                raise self.failure

    def validate_output(
        self, output_path: Path, metadata: dict[str, Any], frame_count: int
    ):
        """Reject truncated stand-ins before the final destination is published.

        Arguments:
            output_path: synthetic concatenated output
            metadata: expected full-source metadata
            frame_count: required output count
        Raises:
            PipeScalerError: if concatenation loses or duplicates frames
        """
        if len(json.loads(output_path.read_text(encoding="utf-8"))) != frame_count:
            raise PipeScalerError("truncated output")


@pytest.fixture
def environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[PipeVideo, CheckpointManager]:
    """Create a source and replace only the final native concatenation boundary.

    Arguments:
        tmp_path: temporary source and checkpoint directory
        monkeypatch: fixture for replacing final FFmpeg execution
    Returns:
        source pipeline object and real checkpoint manager
    """
    path = tmp_path / "source.mkv"
    path.write_bytes(b"original source")
    module = "pipescaler.video.pipelines.segments.checkpointed_video_processor_segment"
    monkeypatch.setattr(f"{module}.val_executable", lambda *_args: Path("ffmpeg"))
    monkeypatch.setattr(
        "pipescaler.video.processors.temporalfix_processor.val_executable",
        Path,
    )
    monkeypatch.setattr(
        "pipescaler.video.processors.temporalfix_processor.run_command",
        lambda command, **_kwargs: (0, f"{command[0]} test-version", ""),
    )

    def concatenate(command: list[str], **_kwargs: Any) -> tuple[int, str, str]:
        """Join recorded frame numbers in manifest order.

        Arguments:
            command: actual generated concatenation command
            **_kwargs: subprocess options
        Returns:
            successful command result
        """
        manifest = Path(command[command.index("-i") + 1])
        frames = []
        for line in manifest.read_text(encoding="utf-8").splitlines()[1:]:
            path = Path(shlex.split(line)[1])
            frames.extend(json.loads(path.read_text(encoding="utf-8")))
        Path(command[-1]).write_text(json.dumps(frames), encoding="utf-8")
        return 0, "", ""

    monkeypatch.setattr(f"{module}.run_command", concatenate)
    return PipeVideo(path=path), CheckpointManager(tmp_path / "checkpoints")


@pytest.mark.parametrize(
    "failure",
    [RuntimeError("native failure"), ValueError("invalid source"), KeyboardInterrupt()],
)
def test_restart_reuses_only_completed_chunks(
    environment: tuple[PipeVideo, CheckpointManager], failure: BaseException
):
    """Resume successful chunks after native failure or Python interruption.

    Arguments:
        environment: source and real checkpoint manager
        failure: interrupted processing condition
    """
    source, manager = environment
    processor = RecordingProcessor()
    processor.failure = failure
    segment = CheckpointedVideoProcessorSegment(processor, manager, chunk_frames=3)
    with pytest.raises(type(failure)):
        segment(source)
    final_path = manager.dir_path / source.location_name / "temporalfix.mkv"
    assert not final_path.exists()
    assert len(list(manager.dir_path.rglob("*.mkv.json"))) == 1
    processor.failure = None
    processor.calls.clear()
    output = segment(source)[0]
    assert processor.calls == [(3, 6), (6, 8)]
    assert output.path is not None
    assert json.loads(output.path.read_text()) == list(range(8))
    assert output.parents == [source]
    processor.calls.clear()
    segment(source)
    assert not processor.calls
    manager.purge_unrecognized_files()
    assert output.path.exists()


def test_changed_settings_model_source_and_corruption_invalidate_cache(
    environment: tuple[PipeVideo, CheckpointManager],
):
    """Distinguish content, model, and settings identities and reject damaged files.

    Arguments:
        environment: source and checkpoint manager
    """
    source, manager = environment
    processor = RecordingProcessor()
    segment = CheckpointedVideoProcessorSegment(processor, manager, chunk_frames=4)
    output = segment(source)[0]
    assert output.path is not None
    output.path.write_bytes(b"truncated")
    processor.calls.clear()
    segment(source)
    assert not processor.calls
    assert json.loads(output.path.read_text()) == list(range(8))
    processor.model_version = "model-two"
    segment(source)
    assert processor.calls == [(0, 4), (4, 8)]
    processor.calls.clear()
    assert source.input_path is not None
    source.input_path.write_bytes(b"different source")
    segment(source)
    assert processor.calls == [(0, 4), (4, 8)]
    changed = RecordingProcessor(strength=1)
    CheckpointedVideoProcessorSegment(changed, manager, chunk_frames=4)(source)
    assert changed.calls == [(0, 4), (4, 8)]


def test_source_change_does_not_publish_or_leave_reusable_chunks(
    environment: tuple[PipeVideo, CheckpointManager],
):
    """Invalidate newly rendered chunks when their source changes mid-run.

    Arguments:
        environment: source and checkpoint manager
    """
    source, manager = environment
    processor = RecordingProcessor()
    processor.change_source = True
    segment = CheckpointedVideoProcessorSegment(processor, manager, chunk_frames=3)
    with pytest.raises(PipeScalerError, match="source changed"):
        segment(source)
    assert not list(manager.dir_path.rglob("*.mkv.json"))
    assert not (manager.dir_path / source.location_name / "temporalfix.mkv").exists()


def test_failed_reprocessing_preserves_previous_valid_destination(
    environment: tuple[PipeVideo, CheckpointManager],
):
    """Retain an older valid final checkpoint when new processing fails.

    Arguments:
        environment: source and checkpoint manager
    """
    source, manager = environment
    first = CheckpointedVideoProcessorSegment(
        RecordingProcessor(), manager, chunk_frames=3
    )(source)[0]
    assert first.path is not None
    original = first.path.read_bytes()
    replacement = RecordingProcessor(strength=1)
    replacement.failure = RuntimeError("new model failed")
    with pytest.raises(RuntimeError):
        CheckpointedVideoProcessorSegment(replacement, manager, chunk_frames=3)(source)
    assert first.path.read_bytes() == original


def test_source_change_during_cache_hit_is_rejected(
    environment: tuple[PipeVideo, CheckpointManager], monkeypatch: pytest.MonkeyPatch
):
    """Recheck mutable sources after hashing a large cached output.

    Arguments:
        environment: source and checkpoint manager
        monkeypatch: fixture for changing the source during cache-hit validation
    """
    source, manager = environment
    processor = RecordingProcessor()
    segment = CheckpointedVideoProcessorSegment(processor, manager, chunk_frames=4)
    output = segment(source)[0]
    assert output.path is not None
    original = output.path.read_bytes()
    hash_file = processor.hash_file

    def mutate_after_hash(path: Path) -> str:
        """Change the source after final-output digest validation begins.

        Arguments:
            path: source or cached output being hashed
        Returns:
            original digest before the concurrent source mutation
        """
        digest = hash_file(path)
        if path == output.path:
            assert source.input_path is not None
            source.input_path.write_bytes(b"changed while verifying the cached output")
        return digest

    monkeypatch.setattr(processor, "hash_file", mutate_after_hash)
    with pytest.raises(PipeScalerError, match="source changed"):
        segment(source)
    assert output.path.read_bytes() == original
