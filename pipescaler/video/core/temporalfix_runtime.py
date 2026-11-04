#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Optional upstream TemporalFix runtime, isolated from ordinary image processing."""

from __future__ import annotations

from fractions import Fraction
from hashlib import file_digest, sha256
from importlib import import_module
from importlib.metadata import version
from os import getenv
from pathlib import Path
from platform import python_version
from typing import Any

import cv2
import numpy as np

from .temporalfix_mps import build_mps_temporal_clip, import_mps_torch
from .temporalfix_settings import TemporalFixSettings
from .video_input import VideoInput

__all__ = [
    "build_temporal_clip",
    "import_temporal_runtime",
    "inspect_temporal_input",
    "temporal_windows",
]


def build_temporal_clip(
    source: VideoInput, settings: TemporalFixSettings, frame_range: tuple[int, int]
) -> Any:
    """Build upstream graphs with three-frame context restricted to each scene.

    Arguments:
        source: video file or ordered image sequence
        settings: validated color, timing, and upstream inference settings
        frame_range: requested half-open source interval
    Returns:
        floating-point RGB VapourSynth node containing only requested frames
    Raises:
        RuntimeError: if optional runtime dependencies or model execution fail
        ValueError: if the requested source interval or input interpretation is invalid
    """
    vs, temporalfix = import_temporal_runtime(settings.backend)
    clip = _open_clip(vs, source, settings)
    pieces = []
    for start, stop, context_start, context_stop in temporal_windows(
        clip.num_frames, frame_range, settings.scene_boundaries
    ):
        window = clip[context_start:context_stop]
        exclusions = (
            " ".join(
                f"[{max(first, context_start) - context_start} "
                f"{min(last, context_stop) - context_start - 1}]"
                for first, last in settings.exclude_ranges
                if first < context_stop and last > context_start
            )
            or None
        )
        if window.num_frames >= 4 and settings.backend == "mps":
            window = build_mps_temporal_clip(
                window,
                strength=settings.strength,
                exclude=exclusions,
                tiles=settings.tiles,
            )
        elif window.num_frames >= 4:
            window = temporalfix.model(
                window,
                strength=settings.strength,
                exclude=exclusions,
                backend=settings.backend,
                tiles=settings.tiles,
                num_streams=settings.num_streams,
                gpu_id=settings.gpu_id,
                engine_folder=settings.engine_folder,
            )
        pieces.append(window[start - context_start : stop - context_start])
    return vs.core.std.Splice(pieces, mismatch=False)


def import_temporal_runtime(backend: str) -> tuple[Any, Any]:
    """Import and validate optional native libraries only inside worker operations.

    Arguments:
        backend: requested upstream execution backend
    Returns:
        VapourSynth and vs_temporalfix modules
    Raises:
        RuntimeError: if dependencies, native plugins, or the backend are unavailable
    """
    try:
        vs: Any = import_module("vapoursynth")
        temporalfix = import_module("vs_temporalfix")
        if version("vs_temporalfix") != "2.4.1":
            raise RuntimeError(
                "This adapter requires vs_temporalfix 2.4.1's seven-frame model API"
            )
        if vs.__version__.release_major < 74:
            raise RuntimeError("VapourSynth R74 or newer is required")
        if backend == "mps":
            import_mps_torch()
        elif backend in {"cpu", "cuda"}:
            torch = import_module("torch")
            if backend == "cuda" and not torch.cuda.is_available():
                raise RuntimeError("CUDA is unavailable in the selected worker")
        elif backend == "tensorrt":
            vs.core.trt.Version()
        else:
            vs.core.ort.Version()
    except (ImportError, AttributeError, OSError) as exc:
        raise RuntimeError(
            "TemporalFix runtime is unavailable; provision VapourSynth R74+, "
            "vs_temporalfix 2.4.1, and the selected backend in the worker environment"
        ) from exc
    return vs, temporalfix


def inspect_temporal_input(
    source: VideoInput, settings: TemporalFixSettings
) -> dict[str, Any]:
    """Inspect native metadata, model fingerprints, and installed runtime versions.

    Arguments:
        source: validated video or sequence input
        settings: input interpretation and selected backend
    Returns:
        JSON-compatible source metadata and runtime identity
    Raises:
        ValueError: if the source cannot satisfy TemporalFix geometry or frame ranges
        RuntimeError: if native dependencies or the requested backend are missing
    """
    vs, temporalfix = import_temporal_runtime(settings.backend)
    clip = _open_clip(vs, source, settings)
    if clip.num_frames < 4 or clip.width % 2 or clip.height % 2:
        raise ValueError(
            "TemporalFix requires at least four frames and even dimensions"
        )
    frame_range = settings.frame_range or (0, clip.num_frames)
    temporal_windows(clip.num_frames, frame_range, settings.scene_boundaries)
    if any(stop > clip.num_frames for _, stop in settings.exclude_ranges):
        raise ValueError("Excluded ranges must lie inside the source")
    model_dir_path = Path(temporalfix.__file__).parent / "models"
    models = {
        path.name: sha256(path.read_bytes()).hexdigest()
        for path in sorted(model_dir_path.rglob("temporalfix_s[0-3]_v*"))
        if path.suffix in {".pth", ".onnx"}
    }
    if not models:
        raise ValueError("TemporalFix model checkpoints are missing")
    packages = ("vs_temporalfix", "vapoursynth", "numpy", "onnx")
    versions = {name: version(name) for name in packages}
    if settings.backend in {"cpu", "cuda", "mps"}:
        versions["torch"] = version("torch")
    else:
        versions[
            "vapoursynth-mlrt-trt"
            if settings.backend == "tensorrt"
            else "vapoursynth-mlrt-ort"
        ] = version(
            "vapoursynth-mlrt-trt"
            if settings.backend == "tensorrt"
            else "vapoursynth-mlrt-ort"
        )
    versions["vapoursynth-core"] = str(vs.__version__)
    versions["python"] = python_version()
    versions["opencv"] = cv2.__version__
    if settings.backend == "mps":
        versions["mps-precision"] = "float32"
        for name in ("PYTORCH_MPS_FAST_MATH", "PYTORCH_MPS_PREFER_METAL"):
            versions[name] = getenv(name, "0")
    plugin_names = ["akarin", "vszip"]
    if source.frame_paths is None:
        plugin_names.append("bs")
    if settings.backend in {"tensorrt", "directml"}:
        plugin_names.append("trt" if settings.backend == "tensorrt" else "ort")
    for name in plugin_names:
        if hasattr(vs.core, name):
            plugin = getattr(vs.core, name)
            versions[f"plugin-{name}"] = str(plugin.version)
            with Path(plugin.plugin_path).open("rb") as stream:
                versions[f"plugin-{name}-sha256"] = file_digest(
                    stream, "sha256"
                ).hexdigest()
    return {
        "width": clip.width,
        "height": clip.height,
        "frames": clip.num_frames,
        "frame_rate": f"{clip.fps_num}/{clip.fps_den}",
        "models": models,
        "versions": versions,
    }


def temporal_windows(
    frame_count: int,
    frame_range: tuple[int, int],
    scene_boundaries: tuple[int, ...] = (),
) -> list[tuple[int, int, int, int]]:
    """Plan requested intervals with radius-three context inside true scene edges.

    Arguments:
        frame_count: total source frames
        frame_range: zero-based half-open requested interval
        scene_boundaries: first frame of each new scene, sorted and unique
    Returns:
        requested start/stop and context start/stop for each intersected scene
    Raises:
        ValueError: if the range or scene boundaries lie outside the source
    """
    start, stop = frame_range
    if not 0 <= start < stop <= frame_count:
        raise ValueError("Frame range must be a nonempty interval inside the source")
    if tuple(sorted(set(scene_boundaries))) != scene_boundaries or any(
        not 0 < boundary < frame_count for boundary in scene_boundaries
    ):
        raise ValueError("Scene boundaries must be sorted indices inside the source")
    edges = (0, *scene_boundaries, frame_count)
    return [
        (
            max(start, left),
            min(stop, right),
            max(left, max(start, left) - 3),
            min(right, min(stop, right) + 3),
        )
        for left, right in zip(edges, edges[1:])
        if start < right and stop > left
    ]


def _open_clip(vs: Any, source: VideoInput, settings: TemporalFixSettings) -> Any:
    """Decode without 8-bit intermediate conversion and apply explicit color rules.

    Arguments:
        vs: imported optional VapourSynth module
        source: video or image-sequence input
        settings: color and rational frame-rate interpretation
    Returns:
        constant-format floating-point RGB clip
    Raises:
        ValueError: if sequence timing/range, image format, or clip format is invalid
        OSError: if a sequence frame cannot be decoded or changes dimensions
        RuntimeError: if the video source plugin is unavailable
    """
    if source.frame_paths is None:
        if not hasattr(vs.core, "bs"):
            raise RuntimeError("Video input requires the VapourSynth BestSource plugin")
        clip = vs.core.bs.VideoSource(
            str(source.input_path), cachemode=0, showprogress=False
        )
    else:
        frame_paths = source.frame_paths
        if settings.frame_rate is None or settings.color_range != "full":
            raise ValueError(
                "Image sequences require an explicit frame rate and full RGB range"
            )
        first = cv2.imread(str(source.frame_paths[0]), cv2.IMREAD_UNCHANGED)
        if first is None or first.ndim != 3 or first.shape[2] != 3:
            raise ValueError("TemporalFix sequences require three-channel RGB images")
        clip = vs.core.std.BlankClip(
            width=first.shape[1],
            height=first.shape[0],
            length=len(source.frame_paths),
            format=vs.RGBS,
        )

        def read_frame(n: int, f: Any) -> Any:
            """Decode one frame lazily, preserving 16-bit image samples.

            Arguments:
                n: zero-based frame position
                f: blank reference frame
            Returns:
                RGB float frame populated in source order
            Raises:
                OSError: if a source frame is invalid or changes geometry
            """
            image = cv2.imread(str(frame_paths[n]), cv2.IMREAD_UNCHANGED)
            if (
                image is None
                or image.shape != first.shape
                or image.dtype not in (np.uint8, np.uint16)
            ):
                raise OSError(
                    "Sequence frame is invalid or changes geometry or sample type"
                )
            result = f.copy()
            for plane in range(3):
                np.copyto(
                    np.asarray(result[plane]),
                    image[:, :, 2 - plane]
                    / (255 if image.dtype == np.uint8 else 65535),
                )
            return result

        clip = vs.core.std.ModifyFrame(clip, clips=clip, selector=read_frame)
    if clip.format is None or clip.width == 0 or clip.height == 0:
        raise ValueError("TemporalFix requires constant dimensions and format")
    if settings.frame_rate is not None:
        rate = Fraction(settings.frame_rate)
        clip = vs.core.std.AssumeFPS(
            clip, fpsnum=rate.numerator, fpsden=rate.denominator
        )
    if clip.fps_num <= 0 or clip.fps_den <= 0:
        raise ValueError("An exact positive frame rate is required")
    options = {
        "format": vs.RGBH if settings.backend in {"tensorrt", "directml"} else vs.RGBS,
        "range_in_s": settings.color_range,
        "range_s": "full",
    }
    if clip.format.color_family != vs.RGB:
        options["matrix_in_s"] = settings.matrix
    return vs.core.resize.Bicubic(clip, **options)
