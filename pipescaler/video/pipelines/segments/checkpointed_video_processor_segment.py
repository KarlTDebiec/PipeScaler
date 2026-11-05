#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Resume rendered video chunks without invoking unsupported PipeVideo.save."""

from __future__ import annotations

import json
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory

from pipescaler.common.file import open_atomic_text_file
from pipescaler.common.subprocess import run_command
from pipescaler.common.validation import val_child_path, val_executable, val_int
from pipescaler.core import PipeScalerError
from pipescaler.core.pipelines import CheckpointManagerBase, Segment
from pipescaler.video.core.pipelines import PipeVideo
from pipescaler.video.core.video_input import VideoInput
from pipescaler.video.processors import TemporalFixProcessor

__all__ = ["CheckpointedVideoProcessorSegment"]


class CheckpointedVideoProcessorSegment(Segment[PipeVideo]):
    """Cache independently validated TemporalFix chunks and publish a complete MKV.

    Cached chunks survive later failures. Every chunk supplies three context frames
    on either side where available, restricted to explicit scene boundaries. Cache
    manifests bind complete file digests to source/model/settings/runtime identities.
    Only completed chunks have manifests; source changes invalidate new manifests.
    The final MKV replaces any previous destination after concatenation validates.
    Concurrent writers to the same checkpoint location are unsupported.
    """

    def __init__(
        self,
        processor: TemporalFixProcessor,
        cp_manager: CheckpointManagerBase,
        checkpoint_name: str = "temporalfix.mkv",
        *,
        chunk_frames: int = 240,
    ):
        """Configure a lossless rendered-video checkpoint.

        Arguments:
            processor: configured upstream library processor
            cp_manager: manager owning the checkpoint root and observed files
            checkpoint_name: relative MKV filename below each input location
            chunk_frames: requested output frames per resumable chunk, at least one
        Raises:
            ValueError: if checkpoint location or chunk length is invalid
        """
        val_child_path(cp_manager.dir_path, checkpoint_name)
        if Path(checkpoint_name).suffix.lower() != ".mkv":
            raise ValueError("Rendered video checkpoints must use the .mkv extension")
        self.processor = processor
        """Library processor whose effective settings determine checkpoint identity."""
        self.cp_manager = cp_manager
        """Manager receiving observations for final output, chunks, and manifests."""
        self.checkpoint_name = checkpoint_name
        """Final checkpoint name relative to the input location."""
        self.chunk_frames = val_int(chunk_frames, min_value=1)
        """Output frames in each restartable chunk; context is additional."""

    def __call__(self, *input_objs: PipeVideo) -> tuple[PipeVideo, ...]:
        """Resume complete chunks, validate the final render, and preserve lineage.

        Concatenation resets timestamps at the exact rational source frame rate;
        MKV timestamps retain the container's millisecond precision.

        Arguments:
            *input_objs: exactly one file-backed video or numbered image sequence
        Returns:
            final video checkpoint with the original input as its parent
        Raises:
            DependencyError: if native dependencies are unavailable
            RuntimeError: if native graph construction or frame evaluation fails
            ValueError: if input count or source representation is unsupported
            PipeScalerError: if inputs change during rendering or output fails
        """
        if len(input_objs) != 1 or input_objs[0].input_path is None:
            raise ValueError(
                "A video processor checkpoint requires one file or sequence input"
            )
        input_obj = input_objs[0]
        source_path = input_obj.input_path
        assert source_path is not None
        source = VideoInput(source_path)
        metadata = self.processor.inspect(source)
        source_identity = self.processor.source_identity(source)
        identity = self.processor.identity(
            source, metadata, source_fingerprint=source_identity
        )
        start, stop = self.processor.settings.frame_range or (0, metadata["frames"])
        location_path = val_child_path(
            self.cp_manager.dir_path, input_obj.location_name
        )
        output_path = val_child_path(location_path, self.checkpoint_name)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if not self._current(output_path, identity):
            chunk_dir_path = (
                output_path.parent / f".{output_path.stem}-chunks" / identity
            )
            chunk_dir_path.mkdir(parents=True, exist_ok=True)
            chunks = []
            created: list[Path] = []
            try:
                for first in range(start, stop, self.chunk_frames):
                    last = min(stop, first + self.chunk_frames)
                    chunk_path = chunk_dir_path / f"{first:09d}-{last:09d}.mkv"
                    chunk_identity = sha256(
                        f"{identity}:{first}:{last}".encode()
                    ).hexdigest()
                    if not self._current(chunk_path, chunk_identity):
                        self.processor.render_range(
                            source, chunk_path, metadata, (first, last)
                        )
                        self._record(chunk_path, chunk_identity)
                        created.append(chunk_path)
                    self._observe(chunk_path)
                    chunks.append(chunk_path)
                self._check_source(source, source_identity, created)
                with TemporaryDirectory(
                    prefix=".video-publish-", dir=output_path.parent
                ) as temporary:
                    scratch_path = Path(temporary) / "complete.mkv"
                    concat_path = Path(temporary) / "chunks.ffconcat"
                    rows = []
                    for path in chunks:
                        name = path.as_posix()
                        if "\n" in name or "\r" in name:
                            raise ValueError(
                                "Checkpoint paths cannot contain newline characters"
                            )
                        rows.append("file '" + name.replace("'", "'\\''") + "'")
                    concat_path.write_text(
                        "ffconcat version 1.0\n" + "\n".join(rows) + "\n",
                        encoding="utf-8",
                    )
                    run_command(
                        [
                            str(val_executable("ffmpeg")),
                            "-v",
                            "error",
                            "-y",
                            "-f",
                            "concat",
                            "-safe",
                            "0",
                            "-i",
                            str(concat_path),
                            "-map",
                            "0:v:0",
                            "-c",
                            "copy",
                            "-bsf:v",
                            f"setts=ts=N*{Fraction(metadata['frame_rate']).denominator}/{Fraction(metadata['frame_rate']).numerator}/TB",
                            str(scratch_path),
                        ],
                    )
                    self.processor.validate_output(scratch_path, metadata, stop - start)
                    self._check_source(source, source_identity, created)
                    scratch_path.replace(output_path)
                self._record(output_path, identity)
            except BaseException:
                self._check_source(source, source_identity, created)
                raise
        self._check_source(source, source_identity, [])
        self._observe(output_path)
        return (PipeVideo(path=output_path, parents=input_obj),)

    def _check_source(
        self, source: VideoInput, expected: list[tuple[str, str]], created: list[Path]
    ):
        """Invalidate new chunk manifests if their source snapshot changes.

        Arguments:
            source: source specification, re-resolved to detect added sequence frames
            expected: source paths and content hashes captured before rendering
            created: chunk paths newly completed during this attempt
        Raises:
            PipeScalerError: if a source changes or disappears during processing
        """
        try:
            if self.processor.source_identity(source) == expected:
                return
        except (OSError, ValueError):
            pass
        for path in created:
            path.with_suffix(".mkv.json").unlink(missing_ok=True)
        raise PipeScalerError("TemporalFix source changed during processing")

    def _current(self, path: Path, identity: str) -> bool:
        """Reuse only an identity-matching manifest and its completed file digest.

        Arguments:
            path: cached video candidate
            identity: effective source/model/settings/range/runtime identity
        Returns:
            whether this is a previously completed, unmodified render
        """
        try:
            manifest = json.loads(
                path.with_suffix(".mkv.json").read_text(encoding="utf-8")
            )
            return manifest["identity"] == identity and manifest[
                "sha256"
            ] == self.processor.hash_file(path)
        except (OSError, ValueError, KeyError, TypeError):
            return False

    def _observe(self, path: Path):
        """Protect rendered data and its manifest during manager cleanup.

        Arguments:
            path: cached or final video path
        """
        for observed in (path, path.with_suffix(".mkv.json")):
            self.cp_manager.observe(
                str(observed.parent.relative_to(self.cp_manager.dir_path)),
                observed.name,
            )

    def _record(self, path: Path, identity: str):
        """Atomically record completion after video decode validation succeeds.

        Arguments:
            path: completed video path
            identity: source/model/settings/range/runtime identity
        """
        with open_atomic_text_file(path.with_suffix(".mkv.json")) as stream:
            json.dump(
                {"identity": identity, "sha256": self.processor.hash_file(path)},
                stream,
                sort_keys=True,
            )
