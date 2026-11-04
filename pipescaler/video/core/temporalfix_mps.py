#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Execute the pinned upstream TemporalFix architecture on Apple MPS in FP32."""

from __future__ import annotations

from collections import OrderedDict
from importlib import import_module
from math import ceil, floor
from os import getenv
from pathlib import Path
from threading import Lock
from typing import Any

import numpy as np

__all__ = [
    "build_mps_temporal_clip",
    "import_mps_torch",
]

_MODEL_FILES = (
    "temporalfix_s0_v1.pth",
    "temporalfix_s1_v1.1.pth",
    "temporalfix_s2_v1.pth",
    "temporalfix_s3_v1.pth",
)


def build_mps_temporal_clip(
    clip: Any, *, strength: float, exclude: str | None, tiles: int
) -> Any:
    """Filter float RGB using upstream weights, tiling, and seven-frame ordering.

    Optional native imports stay inside this worker boundary. Upstream helpers
    define reflected clip edges, tile geometry, and exclusions. Inference is
    serialized per graph; only the current tile is transferred to MPS. No model
    operation falls back to CPU. Weight interpolation and frame IO use CPU FP32.

    Arguments:
        clip: constant-size RGBS VapourSynth clip with at least four frames
        strength: validated suppression strength, rounded to two decimal places
        exclude: upstream inclusive frame-exclusion syntax, or no exclusions
        tiles: validated upstream spatial tile count
    Returns:
        filtered floating-point RGB clip with the original frame count and timing
    Raises:
        ValueError: if the clip geometry or format is unsupported
        RuntimeError: if checkpoints cannot be located or MPS samples are nonfinite
    """
    torch = import_mps_torch()
    vs: Any = import_module("vapoursynth")
    upstream = import_module("vs_temporalfix")
    utils = import_module("vs_temporalfix.utils")
    architecture = import_module("vs_temporalfix.models.temporalfix_arch")
    if (
        clip.format is None
        or clip.format.id != vs.RGBS
        or clip.width < 1
        or clip.height < 1
        or clip.width % 2
        or clip.height % 2
        or clip.num_frames < 4
    ):
        raise ValueError("MPS TemporalFix requires constant even-sized RGBS frames")
    if strength == 0:
        return clip
    overlap = min(64, int(64 * ((clip.width * clip.height) / (1920 * 1080)) ** 0.5))
    tile_width, tile_height, columns, rows = utils.get_tiles(
        clip.width, clip.height, tiles, overlap
    )
    spans = [
        (x0, x1, y0, y1, dx0, dx1, dy0, dy1)
        for y0, y1, dy0, dy1 in utils.get_spans(clip.height, tile_height, rows)
        for x0, x1, dx0, dx1 in utils.get_spans(clip.width, tile_width, columns)
    ]
    if upstream.__file__ is None:
        raise RuntimeError("The TemporalFix checkpoint directory is unavailable")
    model_dir_path = Path(upstream.__file__).parent / "models"
    lower, upper = floor(strength), ceil(strength)
    state = torch.load(
        model_dir_path / _MODEL_FILES[lower], map_location="cpu", weights_only=True
    )
    if lower != upper:
        upper_state = torch.load(
            model_dir_path / _MODEL_FILES[upper], map_location="cpu", weights_only=True
        )
        for key, value in state.items():
            if torch.is_floating_point(value):
                state[key] = torch.lerp(value, upper_state[key], strength - lower)
    model = architecture.temporalfix_arch(
        fixed_hw=(tile_height, tile_width),
        conf_thresh=0.6,
        min_support=1,
        gate_slope=12.0,
        count_slope=4.0,
    )
    model.load_state_dict(state, strict=True)
    model.eval().to(device="mps", dtype=torch.float32)
    del state
    cache: OrderedDict[tuple[int, int], np.ndarray] = OrderedDict()
    lock = Lock()

    def infer(n: int, f: list[Any]) -> Any:
        """Infer one frame with a bounded host cache and serialized MPS model.

        Arguments:
            n: current clip-relative output frame index
            f: upstream-ordered reflected neighbors from minus to plus three
        Returns:
            copied center frame populated with filtered FP32 RGB samples
        Raises:
            RuntimeError: if MPS inference returns nonfinite samples
        """
        with lock, torch.inference_mode():
            output = f[3].copy()
            for tile_index, (x0, x1, y0, y1, dx0, dx1, dy0, dy1) in enumerate(spans):
                neighbors = []
                for offset, frame in enumerate(f):
                    key = (n + offset - 3, tile_index)
                    array = cache.pop(key, None)
                    if array is None:
                        array = np.stack(
                            [
                                np.asarray(frame[plane])[y0:y1, x0:x1]
                                for plane in range(3)
                            ]
                        )
                    cache[key] = array
                    neighbors.append(array)
                    while len(cache) > 10 * tiles:
                        cache.popitem(last=False)
                tensor = torch.from_numpy(np.stack(neighbors)).unsqueeze(0)
                result = model(tensor.to(device="mps", dtype=torch.float32))
                samples = result.detach().cpu().numpy()[0]
                if not np.isfinite(samples).all():
                    raise RuntimeError("MPS TemporalFix produced nonfinite samples")
                for plane in range(3):
                    np.copyto(
                        np.asarray(output[plane])[dy0:dy1, dx0:dx1],
                        samples[plane, dy0 - y0 : dy1 - y0, dx0 - x0 : dx1 - x0],
                    )
            return output

    clamped = utils.basic_expr(clip, expr=["x 0 max 1 min"])
    filtered = vs.core.std.ModifyFrame(
        clamped, clips=utils.gen_shifts(clamped, radius=3), selector=infer
    )
    return utils.exclude_regions(filtered, clip, exclude=exclude)


def import_mps_torch() -> Any:
    """Import PyTorch only when explicit MPS execution is available without fallback.

    Returns:
        PyTorch module with Apple GPU execution available
    Raises:
        RuntimeError: if MPS is unavailable or CPU operator fallback is enabled
    """
    torch = import_module("torch")
    if not torch.backends.mps.is_available():
        raise RuntimeError("MPS is unavailable in the selected worker")
    if getenv("PYTORCH_ENABLE_MPS_FALLBACK") == "1":
        raise RuntimeError("MPS CPU fallback must be disabled")
    return torch
