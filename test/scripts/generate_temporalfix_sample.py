#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Generate small 16-bit RGB animation-like samples for optional TemporalFix checks."""

from __future__ import annotations

from pathlib import Path
from subprocess import run

import cv2
import numpy as np

from pipescaler.common.validation import val_executable

__all__ = ["generate_temporalfix_sample", "generate_temporalfix_yuv_video"]


def generate_temporalfix_sample(dir_path: Path, frame_count: int = 12) -> Path:
    """Write numbered PNGs with colored backgrounds, line jitter, and a scene cut.

    Arguments:
        dir_path: output directory for generated test assets
        frame_count: number of frames to generate
    Returns:
        numbered sequence template suitable for VideoInput
    Raises:
        OSError: if a generated frame cannot be written
    """
    dir_path.mkdir(parents=True, exist_ok=True)
    for number in range(frame_count):
        rgb = np.full((32, 32, 3), (0.123456, 0.345678, 0.789012), np.float64)
        if number >= 7:
            rgb[:] = (0.8, 0.25, 0.12)
        rgb[8:24, 10:12] = 0.15 + (number % 2) * 0.015
        rgb[15:17, 8:24] = 0.65 - (number % 3) * 0.01
        bgr = np.rint(rgb[:, :, ::-1] * 65535).astype(np.uint16)
        if not cv2.imwrite(str(dir_path / f"frame_{number:04d}.png"), bgr):
            raise OSError("Cannot write generated TemporalFix fixture")
    return dir_path / "frame_%04d.png"


def generate_temporalfix_yuv_video(template: Path, output_path: Path):
    """Encode a limited-range BT.709 sample to exercise real video color conversion.

    Arguments:
        template: generated numbered 16-bit PNG source
        output_path: lossless YUV test video destination
    """
    run(
        [
            str(val_executable("ffmpeg")),
            "-v",
            "error",
            "-y",
            "-framerate",
            "24000/1001",
            "-i",
            str(template),
            "-vf",
            "scale=out_color_matrix=bt709:out_range=tv",
            "-c:v",
            "ffv1",
            "-pix_fmt",
            "yuv420p10le",
            "-color_range",
            "tv",
            "-colorspace",
            "bt709",
            "-color_primaries",
            "bt709",
            "-color_trc",
            "bt709",
            str(output_path),
        ],
        check=True,
        capture_output=True,
    )
