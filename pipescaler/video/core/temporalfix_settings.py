#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Validated settings shared with the optional TemporalFix worker."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

from pipescaler.common.validation import val_float, val_int, val_str

__all__ = ["TemporalFixSettings"]


@dataclass(frozen=True, kw_only=True)
class TemporalFixSettings:
    """Temporal processing and explicit input color/timing interpretation.

    Frame ranges are zero-based half-open intervals. Scene boundaries are indices
    of the first frame in each new scene. Scenes shorter than four frames pass
    through unchanged; upstream model inference requires at least four frames.
    """

    matrix: str
    """Input YUV matrix: 709, 470bg, 170m, or 2020ncl; ignored for RGB sources."""
    color_range: str
    """Input sample range: limited or full; RGB image sequences require full."""
    strength: float = 2.0
    """Upstream suppression strength from zero to three, rounded to two decimals."""
    backend: str = "cpu"
    """Upstream cpu, cuda, directml, or tensorrt execution backend."""
    tiles: int = 1
    """Upstream spatial tile count, independent of temporal chunk length."""
    num_streams: int = 1
    """Upstream parallel inference stream count."""
    gpu_id: int = 0
    """Zero-based GPU index, unused by the CPU backend."""
    engine_folder: str | None = None
    """Optional TensorRT engine-cache directory."""
    frame_rate: str | None = None
    """Exact rational frame rate, required for sequences; video defaults to native."""
    frame_range: tuple[int, int] | None = None
    """Requested source interval, or the full source when unset."""
    exclude_ranges: tuple[tuple[int, int], ...] = ()
    """Source intervals passed through by upstream exclusion handling."""
    scene_boundaries: tuple[int, ...] = ()
    """Explicit scene cuts across which temporal context must not flow."""

    def __post_init__(self):
        """Validate settings before starting an optional runtime.

        Raises:
            ValueError: if color, timing, ranges, or inference settings are invalid
        """
        val_str(self.matrix, options=("709", "470bg", "170m", "2020ncl"))
        val_str(self.color_range, options=("limited", "full"))
        val_str(self.backend, options=("cpu", "cuda", "directml", "tensorrt"))
        object.__setattr__(
            self,
            "strength",
            round(val_float(self.strength, min_value=0, max_value=3, finite=True), 2),
        )
        object.__setattr__(self, "tiles", val_int(self.tiles, min_value=1))
        object.__setattr__(self, "num_streams", val_int(self.num_streams, min_value=1))
        object.__setattr__(self, "gpu_id", val_int(self.gpu_id, min_value=0))
        if self.frame_rate is not None:
            try:
                rate = Fraction(self.frame_rate)
            except (ValueError, ZeroDivisionError) as exc:
                raise ValueError(
                    "Frame rate must be an exact positive rational"
                ) from exc
            if rate <= 0:
                raise ValueError("Frame rate must be positive")
            object.__setattr__(self, "frame_rate", str(rate))
        if self.engine_folder is not None:
            object.__setattr__(
                self, "engine_folder", str(Path(self.engine_folder).resolve())
            )
        if self.frame_range is not None:
            object.__setattr__(
                self, "frame_range", self._validate_interval(self.frame_range)
            )
        object.__setattr__(
            self,
            "exclude_ranges",
            tuple(
                self._validate_interval(interval) for interval in self.exclude_ranges
            ),
        )
        boundaries = tuple(
            val_int(boundary, min_value=1) for boundary in self.scene_boundaries
        )
        if tuple(sorted(set(boundaries))) != boundaries:
            raise ValueError("Scene boundaries must be sorted and unique")
        object.__setattr__(self, "scene_boundaries", boundaries)

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-compatible settings with effective upstream strength.

        Returns:
            settings suitable for worker requests and checkpoint identity
        """
        return asdict(self)

    @staticmethod
    def _validate_interval(interval: tuple[int, int]) -> tuple[int, int]:
        """Normalize a nonempty zero-based half-open source interval.

        Arguments:
            interval: start and exclusive stop indices
        Returns:
            validated immutable interval
        Raises:
            ValueError: if the interval has invalid dimensions or endpoints
        """
        if len(interval) != 2:
            raise ValueError("Frame intervals require start and stop indices")
        start = val_int(interval[0], min_value=0)
        return start, val_int(interval[1], min_value=start + 1)
