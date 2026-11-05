#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Run upstream TemporalFix in an explicitly selected optional Python environment."""

from __future__ import annotations

import json
import os
import sys
from fractions import Fraction
from hashlib import file_digest, sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from pipescaler.common import package_root
from pipescaler.common.subprocess import run_command
from pipescaler.common.validation import val_executable, val_input_path
from pipescaler.core import PipeScalerError, Runner
from pipescaler.video.core.temporalfix_settings import TemporalFixSettings
from pipescaler.video.core.video_input import VideoInput

__all__ = ["TemporalFixRunner"]


class TemporalFixRunner(Runner[VideoInput | Path | str]):
    """Render lossless 16-bit RGB checkpoints through upstream vs_temporalfix.

    The worker may use a Python 3.13 or 3.14 environment containing VapourSynth,
    vs_temporalfix, the selected backend, OpenCV, and BestSource for video files.
    FFmpeg and ffprobe are required. Encoding contains video only; delivery codecs,
    audio, and subtitles remain project concerns. Inputs must have constant timing.
    """

    def __init__(
        self,
        settings: TemporalFixSettings,
        *,
        worker_python_path: Path | str = sys.executable,
        timeout: int = 600,
    ):
        """Store validated settings without importing native video dependencies.

        Arguments:
            settings: explicit color/timing and upstream processing configuration
            worker_python_path: interpreter containing the optional worker runtime
            timeout: seconds allowed per worker or output-validation operation
        """
        super().__init__(timeout)
        self.settings = settings
        """Validated upstream processing and input-interpretation settings."""
        self.worker_python_path = val_input_path(worker_python_path)
        """Interpreter used for native video processing, independent of image tools."""

    def __repr__(self) -> str:
        """Return a reconstructible worker configuration.

        Returns:
            constructor expression including settings and selected interpreter
        """
        return (
            f"TemporalFixRunner(settings={self.settings!r}, "
            f"worker_python_path={str(self.worker_python_path)!r}, "
            f"timeout={self.timeout!r})"
        )

    def get_command(
        self, input_path: VideoInput | Path | str, output_path: Path
    ) -> list[str]:
        """Build literal worker tokens referencing the prepared request file.

        Arguments:
            input_path: concrete video or numbered sequence specification
            output_path: scratch output beside its .request.json settings file
        Returns:
            worker interpreter invocation without shell quoting
        """
        source = (
            input_path if isinstance(input_path, VideoInput) else VideoInput(input_path)
        )
        return [
            str(self.worker_python_path),
            "-m",
            "pipescaler.video.runners.temporalfix_worker",
            "--input",
            str(source.input_path),
            "--output",
            str(output_path),
            "--request",
            str(output_path.with_suffix(".request.json")),
        ]

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
            source_fingerprint: optional previously captured source snapshot
        Returns:
            SHA256 identity used for checkpoint invalidation
        """
        adapter_paths = (
            Path(__file__),
            Path(__file__).with_name("temporalfix_worker.py"),
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
                tool: run_command(
                    [str(val_executable(tool)), "-version"], timeout=self.timeout
                )[1].splitlines()[0]
                for tool in ("ffmpeg", "ffprobe")
            },
        }
        return sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

    def inspect(self, input_path: VideoInput | Path | str) -> dict[str, Any]:
        """Probe the selected optional runtime and exact input metadata.

        Arguments:
            input_path: video or numbered image sequence to inspect
        Returns:
            source geometry/count/rate and dependency/model identity
        Raises:
            PipeScalerError: if the worker or optional runtime cannot inspect the input
        """
        interpreter_version = self._execute(
            [
                str(self.worker_python_path),
                "-c",
                "import sys; print('.'.join(map(str, sys.version_info[:2])))",
            ]
        ).strip()
        if tuple(map(int, interpreter_version.split("."))) < (3, 13):
            raise PipeScalerError(
                "The selected TemporalFix worker requires Python 3.13 or newer"
            )
        with TemporaryDirectory(prefix="pipescaler-temporal-probe-") as temporary:
            output_path = Path(temporary) / "probe.mkv"
            request_path = output_path.with_suffix(".request.json")
            request_path.write_text(
                json.dumps({"settings": self.settings.to_dict()}), encoding="utf-8"
            )
            command = self.get_command(input_path, output_path) + ["--probe"]
            stdout = self._execute(command)
            try:
                return self._validate_metadata(
                    json.loads(stdout.strip().splitlines()[-1])
                )
            except (ValueError, IndexError) as exc:
                raise PipeScalerError(
                    "TemporalFix worker returned invalid inspection metadata"
                ) from exc

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
            output_path: completed MKV destination, replaced after successful validation
            metadata: expected full-source geometry and exact rational rate
            frame_range: half-open source range; worker supplies and trims context
        Raises:
            PipeScalerError: if processing or validation fails
        """
        output_path = output_path.resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with TemporaryDirectory(
            prefix=".temporalfix-", dir=output_path.parent
        ) as temporary:
            scratch_path = Path(temporary) / "render.mkv"
            request = {
                "settings": self.settings.to_dict(),
                "metadata": metadata,
                "frame_range": frame_range,
                "ffmpeg": str(val_executable("ffmpeg")),
            }
            scratch_path.with_suffix(".request.json").write_text(
                json.dumps(request), encoding="utf-8"
            )
            self._execute(self.get_command(source, scratch_path))
            self.validate_output(
                scratch_path, metadata, frame_range[1] - frame_range[0]
            )
            scratch_path.replace(output_path)

    def run(self, input_path: VideoInput | Path | str, output_path: Path):
        """Render the selected source range through the upstream worker.

        Arguments:
            input_path: video or ordered sequence input
            output_path: completed lossless RGB MKV destination
        Raises:
            PipeScalerError: if sources change or worker/render validation fails
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
                timeout=self.timeout,
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
            (str(path), TemporalFixRunner.hash_file(path))
            for path in current.frame_paths or (current.input_path,)
        ]

    def _execute(self, command: list[str]) -> str:
        """Run a managed worker process with this package visible to its interpreter.

        Arguments:
            command: literal subprocess tokens
        Returns:
            captured worker standard output
        Raises:
            PipeScalerError: if the worker fails, is unavailable, or times out
        """
        env = dict(os.environ)
        env["PYTHONPATH"] = os.pathsep.join(
            filter(None, (str(package_root.parent), env.get("PYTHONPATH")))
        )
        env["PYTHONUTF8"] = "1"
        try:
            return run_command(command, timeout=self.timeout, env=env)[1]
        except (OSError, ValueError) as exc:
            raise PipeScalerError(f"TemporalFix worker failed: {exc}") from exc

    @staticmethod
    def _validate_metadata(value: object) -> dict[str, Any]:
        """Validate the worker's JSON boundary before using source metadata.

        Arguments:
            value: decoded inspection response from the worker
        Returns:
            complete source geometry, rational timing, and runtime/model metadata
        Raises:
            ValueError: if required fields or their values are malformed
        """
        if not isinstance(value, dict):
            raise ValueError("Worker inspection must return an object")
        if any(
            type(value.get(key)) is not int or value[key] <= 0
            for key in ("width", "height", "frames")
        ):
            raise ValueError(
                "Worker inspection must return positive integer geometry/count"
            )
        try:
            if (
                not isinstance(value["frame_rate"], str)
                or Fraction(value["frame_rate"]) <= 0
            ):
                raise ValueError("Worker frame rate must be an exact positive rational")
            for key in ("models", "versions"):
                entries = value[key]
                if (
                    not isinstance(entries, dict)
                    or not entries
                    or any(
                        not isinstance(name, str)
                        or not isinstance(item, str)
                        or not item
                        for name, item in entries.items()
                    )
                ):
                    raise ValueError("Worker model/version fingerprints are invalid")
        except (KeyError, TypeError, ZeroDivisionError) as exc:
            raise ValueError(
                "Worker inspection metadata is incomplete or invalid"
            ) from exc
        return value
