#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Represent a video file or a validated numbered image sequence."""

from __future__ import annotations

import re
from os.path import expanduser, expandvars
from pathlib import Path

import cv2

from pipescaler.common.validation import val_input_path

from .image_sequence_capture import ImageSequenceCapture

__all__ = ["VideoInput"]


class VideoInput:
    """A concrete video file or one `%d` or `%0Nd` numbered-path template.

    The placeholder may occur anywhere in one filename or directory component.
    Width is a minimum, matching printf formatting. Indices are nonnegative and
    contiguous, with any starting index. Shell globs and multiple placeholders are
    unsupported. Existing literal files take precedence over pattern parsing.
    """

    def __init__(self, input_path: Path | str):
        """Resolve a file or sequence without opening its decoder.

        Arguments:
            input_path: video file or numbered image-sequence template
        Raises:
            FileNotFoundError: if the input file or matching frames do not exist
            ValueError: if a template is malformed or frame numbering has gaps
        """
        self.input_path = Path(expandvars(expanduser(str(input_path)))).resolve()
        """Absolute concrete file path or sequence template."""
        self.frame_paths: tuple[Path, ...] | None = None
        """Numerically ordered frames, or None for a concrete video file."""
        self.name = self.input_path.stem
        """File stem or containing sequence directory name."""
        if self.input_path.is_file() or "%" not in str(self.input_path):
            self.input_path = val_input_path(self.input_path)
            return

        placeholders = list(re.finditer(r"%(?:0[1-9][0-9]*)?d", str(self.input_path)))
        remainder = re.sub(r"%(?:0[1-9][0-9]*)?d", "", str(self.input_path))
        if len(placeholders) != 1 or "%" in remainder:
            raise ValueError("Use exactly one %d or %0Nd image-sequence placeholder.")
        component_index = next(
            index for index, part in enumerate(self.input_path.parts) if "%" in part
        )
        root_path = Path(*self.input_path.parts[:component_index])
        component = self.input_path.parts[component_index]
        placeholder = placeholders[0].group()
        prefix, suffix = component.split(placeholder)
        pattern = re.compile(f"{re.escape(prefix)}([0-9]+){re.escape(suffix)}")
        width = int(placeholder[2:-1]) if placeholder != "%d" else 0
        matches: list[tuple[int, Path]] = []
        if root_path.is_dir():
            for candidate_path in root_path.iterdir():
                match = pattern.fullmatch(candidate_path.name)
                if match is None:
                    continue
                number = int(match[1])
                if candidate_path.name != f"{prefix}{number:0{width}d}{suffix}":
                    continue
                frame_path = candidate_path.joinpath(
                    *self.input_path.parts[component_index + 1 :]
                )
                if frame_path.is_file():
                    matches.append((number, frame_path))
        if not matches:
            raise FileNotFoundError(
                f"No image-sequence frames match '{self.input_path}'."
            )
        matches.sort()
        for (previous, _), (current, _) in zip(matches, matches[1:], strict=False):
            if current != previous + 1:
                raise ValueError(
                    f"Missing image-sequence frame {previous + 1} "
                    f"in '{self.input_path}'."
                )
        self.frame_paths = tuple(path for _, path in matches)
        self.name = root_path.name or "frames"

    def __repr__(self) -> str:
        """Return a reconstructible input specification.

        Returns:
            constructor expression for this file or sequence
        """
        return f"{self.__class__.__name__}(input_path={str(self.input_path)!r})"

    def open_capture(self) -> cv2.VideoCapture | ImageSequenceCapture:
        """Open a new capture owned by the caller.

        Returns:
            opened file or image-sequence capture
        Raises:
            OSError: if the video or first image cannot be decoded
        """
        if self.frame_paths is not None:
            return ImageSequenceCapture(self.frame_paths)
        capture = cv2.VideoCapture(str(self.input_path))
        try:
            if not capture.isOpened():
                raise OSError(f"Cannot open video '{self.input_path}'.")
        except BaseException:
            capture.release()
            raise
        return capture
