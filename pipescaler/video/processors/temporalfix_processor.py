#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""TemporalFix video processing and lossless RGB publication."""

from __future__ import annotations

import json
from contextlib import suppress
from fractions import Fraction
from hashlib import file_digest, sha256
from pathlib import Path
from shlex import split
from subprocess import DEVNULL, PIPE, Popen
from tempfile import TemporaryDirectory, TemporaryFile
from typing import Any

import numpy as np

from pipescaler.common import package_root
from pipescaler.common.subprocess import run_command
from pipescaler.common.validation import val_executable
from pipescaler.core import PipeScalerError
from pipescaler.video.core.temporalfix_runtime import (
    build_temporal_clip,
    inspect_temporal_input,
)
from pipescaler.video.core.temporalfix_settings import TemporalFixSettings
from pipescaler.video.core.video_input import VideoInput

__all__ = ["TemporalFixProcessor"]


class TemporalFixProcessor:
    """Render lossless 16-bit RGB checkpoints through upstream vs_temporalfix.

    Install dependencies with `uv sync --extra temporalfix`. A native VapourSynth
    runtime and FFmpeg/ffprobe on PATH are required; video files need BestSource.
    Inputs must have constant timing. Output rounds floating-point RGB once to
    16-bit planar samples and encodes losslessly as FFV1 in MKV, omitting audio
    and subtitles.
    """

    def __init__(self, settings: TemporalFixSettings):
        """Store processing settings.

        Arguments:
            settings: explicit color/timing and upstream processing configuration
        """
        self.settings = settings
        """TemporalFix processing and input settings."""

    def __repr__(self) -> str:
        """Return a reconstructible processor configuration.

        Returns:
            constructor expression including effective settings
        """
        return f"TemporalFixProcessor(settings={self.settings!r})"

    def identity(
        self,
        source: VideoInput,
        metadata: dict[str, Any],
        *,
        source_fingerprint: list[tuple[str, str]] | None = None,
    ) -> str:
        """Fingerprint sources, effective settings, models, runtime, and adapter code.

        Arguments:
            source: video file or numerically ordered image sequence
            metadata: probed metadata and native runtime/model fingerprints
            source_fingerprint: previously captured source snapshot, if available
        Returns:
            SHA256 identity used for checkpoint invalidation
        """
        adapter_paths = (
            Path(__file__),
            package_root / "core/dependencies/temporalfix.py",
            package_root / "video/core/temporalfix_runtime.py",
            package_root / "video/core/temporalfix_settings.py",
        )
        payload = {
            "source": self.source_identity(source)
            if source_fingerprint is None
            else source_fingerprint,
            "settings": self.settings.to_dict(),
            "metadata": metadata,
            "adapter": [self.hash_file(path) for path in adapter_paths],
            "encoding_tools": {
                tool: run_command([str(val_executable(tool)), "-version"])[
                    1
                ].splitlines()[0]
                for tool in ("ffmpeg", "ffprobe")
            },
        }
        return sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

    def inspect(self, input_path: VideoInput | Path | str) -> dict[str, Any]:
        """Inspect source metadata and runtime fingerprints.

        Arguments:
            input_path: video or numbered image sequence to inspect
        Returns:
            source geometry/count/rate and dependency/model identity
        Raises:
            DependencyError: if runtime dependencies are unavailable
            RuntimeError: if native dependencies or the backend are unavailable
            ValueError: if source interpretation or settings are invalid
        """
        source = (
            input_path if isinstance(input_path, VideoInput) else VideoInput(input_path)
        )
        return inspect_temporal_input(source, self.settings)

    def process(self, input_path: VideoInput | Path | str, output_path: Path):
        """Render the selected source range to a lossless RGB MKV.

        Arguments:
            input_path: video or ordered sequence input
            output_path: completed lossless RGB MKV destination
        Raises:
            DependencyError: if runtime dependencies are unavailable
            RuntimeError: if native processing fails
            ValueError: if source interpretation or settings are invalid
            PipeScalerError: if sources change or output validation fails
        """
        source = (
            input_path if isinstance(input_path, VideoInput) else VideoInput(input_path)
        )
        metadata = self.inspect(source)
        source_identity = self.source_identity(source)
        output_path = output_path.resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with TemporaryDirectory(
            prefix=".temporalfix-source-", dir=output_path.parent
        ) as temporary:
            scratch_path = Path(temporary) / "checked.mkv"
            self.render_range(
                source,
                scratch_path,
                metadata,
                self.settings.frame_range or (0, metadata["frames"]),
            )
            if self.source_identity(source) != source_identity:
                raise PipeScalerError("TemporalFix source changed during processing")
            scratch_path.replace(output_path)

    def render_range(
        self,
        source: VideoInput,
        output_path: Path,
        metadata: dict[str, Any],
        frame_range: tuple[int, int],
    ):
        """Render, decode-validate, and atomically publish a source interval.

        Arguments:
            source: validated input specification
            output_path: MKV destination, replaced after successful validation
            metadata: expected full-source geometry and exact rational rate
            frame_range: half-open source range with scene-aware context and trimming
        Raises:
            DependencyError: if runtime dependencies are unavailable
            RuntimeError: if native graph construction or frame evaluation fails
            ValueError: if source interpretation or settings are invalid
            PipeScalerError: if metadata changes, encoding fails, or validation fails
        """
        if self.inspect(source) != metadata:
            raise PipeScalerError("Source metadata or runtime changed after inspection")
        output_path = output_path.resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with TemporaryDirectory(
            prefix=".temporalfix-", dir=output_path.parent
        ) as temporary:
            scratch_path = Path(temporary) / "render.mkv"
            clip = build_temporal_clip(source, self.settings, frame_range)
            command = [
                str(val_executable("ffmpeg")),
                *split(
                    f"""
                    -v error -y
                    -f rawvideo -pixel_format gbrp16le
                    -video_size {clip.width}x{clip.height}
                    -framerate {metadata["frame_rate"]}
                    -i pipe:0 -an -sn
                    -c:v ffv1 -level 3
                    -pix_fmt gbrp16le -color_range pc -colorspace rgb
                    -f matroska
                    """
                ),
                str(scratch_path),
            ]
            self._encode_clip(clip, command)
            self.validate_output(
                scratch_path, metadata, frame_range[1] - frame_range[0]
            )
            scratch_path.replace(output_path)

    def validate_output(
        self, output_path: Path, metadata: dict[str, Any], frame_count: int
    ):
        """Decode all frames and reject truncated, mis-sized, or mistimed output.

        Arguments:
            output_path: rendered lossless video to validate
            metadata: expected source dimensions and rational frame rate
            frame_count: exact expected output count
        Raises:
            PipeScalerError: if output cannot be completely decoded or metadata differs
        """
        try:
            _, stdout, stderr = run_command(
                [
                    str(val_executable("ffprobe")),
                    "-v",
                    "error",
                    "-select_streams",
                    "v:0",
                    "-count_frames",
                    "-show_frames",
                    "-show_entries",
                    "stream=width,height,nb_read_frames,avg_frame_rate,time_base,codec_name,pix_fmt,color_range:frame=best_effort_timestamp",
                    "-of",
                    "json",
                    str(output_path),
                ],
            )
            probe = json.loads(stdout)
            stream = probe["streams"][0]
            rate = Fraction(metadata["frame_rate"])
            time_base = Fraction(stream["time_base"])
            frames = probe["frames"]
            if (
                stderr
                or int(stream["nb_read_frames"]) != frame_count
                or stream["width"] != metadata["width"]
                or stream["height"] != metadata["height"]
                or Fraction(stream["avg_frame_rate"])
                != Fraction(metadata["frame_rate"])
                or stream["codec_name"] != "ffv1"
                or stream["pix_fmt"] != "gbrp16le"
                or stream["color_range"] != "pc"
                or len(frames) != frame_count
                or rate <= 0
                or time_base <= 0
            ):
                raise ValueError(
                    "Rendered video has incorrect dimensions, frame count, or timing"
                )
            for number, frame in enumerate(frames):
                if (
                    abs(int(frame["best_effort_timestamp"]) * time_base - number / rate)
                    > time_base
                ):
                    raise ValueError(
                        "Rendered frame timestamps do not preserve rational timing"
                    )
        except (
            OSError,
            ValueError,
            KeyError,
            IndexError,
            TypeError,
            ZeroDivisionError,
        ) as exc:
            raise PipeScalerError(
                f"TemporalFix output validation failed: {output_path}"
            ) from exc

    @staticmethod
    def hash_file(path: Path) -> str:
        """Hash file contents without loading a video into memory.

        Arguments:
            path: existing file to fingerprint
        Returns:
            hexadecimal SHA256 digest
        """
        with path.open("rb") as stream:
            return file_digest(stream, "sha256").hexdigest()

    @staticmethod
    def source_identity(source: VideoInput) -> list[tuple[str, str]]:
        """Re-resolve sequences and fingerprint every source in frame order.

        Arguments:
            source: original video or sequence specification
        Returns:
            absolute source paths and content digests in playback order
        """
        current = VideoInput(source.input_path)
        return [
            (str(path), TemporalFixProcessor.hash_file(path))
            for path in current.frame_paths or (current.input_path,)
        ]

    @staticmethod
    def _encode_clip(clip: Any, command: list[str]):
        """Stream final 16-bit samples while avoiding encoder stderr pipe deadlocks.

        Frame failures and interruption terminate and reap the encoder.

        Arguments:
            clip: floating-point RGB VapourSynth output
            command: FFmpeg raw-video encoder command
        Raises:
            PipeScalerError: if FFmpeg rejects samples or exits unsuccessfully
            RuntimeError: if native frame evaluation fails
        """
        with TemporaryFile() as log:
            process = Popen(command, stdin=PIPE, stdout=DEVNULL, stderr=log)
            try:
                assert process.stdin is not None
                for number in range(clip.num_frames):
                    with clip.get_frame(number) as frame:
                        # FFmpeg planar GBR differs from VapourSynth planar RGB
                        for plane in (1, 2, 0):
                            samples = np.asarray(frame[plane], dtype=np.float32)
                            process.stdin.write(
                                np.rint(np.clip(samples, 0, 1) * 65535)
                                .astype("<u2")
                                .tobytes()
                            )
                process.stdin.close()
                if process.wait() != 0:
                    log.seek(0)
                    message = log.read().decode(errors="replace")
                    raise PipeScalerError(f"TemporalFix encoding failed: {message}")
            except BrokenPipeError as exc:
                process.wait()
                log.seek(0)
                message = log.read().decode(errors="replace")
                raise PipeScalerError(
                    f"TemporalFix encoder rejected input: {message}"
                ) from exc
            finally:
                if process.poll() is None:
                    process.kill()
                process.wait()
                if process.stdin is not None and not process.stdin.closed:
                    with suppress(BrokenPipeError):
                        process.stdin.close()
