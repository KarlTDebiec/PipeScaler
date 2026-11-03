#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Internal optional-runtime worker; render through upstream TemporalFix."""

from __future__ import annotations

import json
from argparse import ArgumentParser
from contextlib import suppress
from pathlib import Path
from subprocess import DEVNULL, PIPE, Popen
from tempfile import TemporaryFile
from typing import Any

import numpy as np

from pipescaler.video.core.temporalfix_runtime import (
    build_temporal_clip,
    inspect_temporal_input,
)
from pipescaler.video.core.temporalfix_settings import TemporalFixSettings
from pipescaler.video.core.video_input import VideoInput

__all__ = ["main"]


def main():
    """Inspect or render one validated worker request.

    Raises:
        RuntimeError: if the source changes or FFmpeg encoding fails
    """
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--request", required=True, type=Path)
    parser.add_argument("--probe", action="store_true")
    args = parser.parse_args()
    request = json.loads(args.request.read_text(encoding="utf-8"))
    settings = _settings(request["settings"])
    source = VideoInput(args.input)
    metadata = inspect_temporal_input(source, settings)
    if args.probe:
        print(json.dumps(metadata, sort_keys=True))
        return
    if metadata != request["metadata"]:
        raise RuntimeError("Source metadata or runtime changed after inspection")
    frame_range = tuple(request["frame_range"])
    clip = build_temporal_clip(source, settings, frame_range)
    command = [
        request["ffmpeg"],
        "-v",
        "error",
        "-y",
        "-f",
        "rawvideo",
        "-pixel_format",
        "gbrp16le",
        "-video_size",
        f"{clip.width}x{clip.height}",
        "-framerate",
        metadata["frame_rate"],
        "-i",
        "pipe:0",
        "-an",
        "-sn",
        "-c:v",
        "ffv1",
        "-level",
        "3",
        "-pix_fmt",
        "gbrp16le",
        "-color_range",
        "pc",
        "-colorspace",
        "rgb",
        "-f",
        "matroska",
        str(args.output),
    ]
    _encode_clip(clip, command)


def _encode_clip(clip: Any, command: list[str]):
    """Stream final 16-bit samples while avoiding encoder stderr pipe deadlocks.

    The parent runner owns timeout/cancellation of the worker's entire process tree.

    Arguments:
        clip: floating-point RGB VapourSynth output
        command: FFmpeg raw-video encoder command
    Raises:
        RuntimeError: if FFmpeg rejects samples or exits unsuccessfully
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
                raise RuntimeError(f"TemporalFix encoding failed: {message}")
        except BrokenPipeError as exc:
            process.wait()
            log.seek(0)
            message = log.read().decode(errors="replace")
            raise RuntimeError(
                f"TemporalFix encoder rejected input: {message}"
            ) from exc
        finally:
            if process.poll() is None:
                process.kill()
            process.wait()
            if process.stdin is not None and not process.stdin.closed:
                with suppress(BrokenPipeError):
                    process.stdin.close()


def _settings(raw: dict[str, Any]) -> TemporalFixSettings:
    """Restore immutable interval collections from a JSON worker request.

    Arguments:
        raw: serialized validated settings
    Returns:
        settings with tuple ranges and exact rational timing
    """
    raw["scene_boundaries"] = tuple(raw.get("scene_boundaries", ()))
    raw["exclude_ranges"] = tuple(tuple(pair) for pair in raw.get("exclude_ranges", ()))
    if raw.get("frame_range") is not None:
        raw["frame_range"] = tuple(raw["frame_range"])
    return TemporalFixSettings(**raw)


if __name__ == "__main__":
    main()
