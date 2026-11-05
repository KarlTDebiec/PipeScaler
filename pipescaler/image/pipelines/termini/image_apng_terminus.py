#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Collects ordered image frames into an animated PNG using libapngasm."""

from __future__ import annotations

from contextlib import ExitStack
from fractions import Fraction
from os import name as os_name
from pathlib import Path
from shutil import copyfile
from tempfile import gettempdir
from types import TracebackType
from typing import Self

import numpy as np
from apngasm_python.apngasm import APNGAsmBinder
from numpy.typing import NDArray
from PIL import Image

from pipescaler.common.file import get_temp_file_path
from pipescaler.common.validation import val_output_path
from pipescaler.core.exceptions import PipeScalerError
from pipescaler.image.core.pipelines import ImageTerminus, PipeImage

__all__ = ["ImageApngTerminus"]


class ImageApngTerminus(ImageTerminus):
    """Collect image frames into an animated PNG published on successful context exit.

    Use a `with` block. Each call snapshots one static `PipeImage` as a frame in
    arrival order. Dimensions must match and be nonzero. Names and locations do
    not affect frame order. Inputs are not modified. Native frame buffers are
    retained until context exit; instances are single-use.

    Consecutive visually identical playback frames combine using exact rational
    timing; their reduced total delay must fit APNG's 16-bit numerator and
    denominator. Hidden RGB under zero alpha is discarded. One distinct playback
    frame without a fallback produces a static PNG.

    The output directory is created on entry. Encoding, decoding, and native
    cleanup complete before atomic publication. Body exceptions or frame failures
    preserve any existing destination, including when a frame error is caught
    inside the context. Empty collections are rejected.

    Native encoding uses the system temporary directory. On Windows, a non-ASCII
    temporary directory instead requires a writable current working directory,
    where encoding uses an ASCII filename without changing cwd.
    """

    def __init__(
        self,
        output_path: Path | str,
        *,
        delay: tuple[int, int] = (1, 10),
        loops: int = 0,
        skip_first: bool = False,
    ):
        """Validate and store the animation's destination and default settings.

        Arguments:
            output_path: destination with a .png or .apng suffix
            delay: default (numerator, denominator) in seconds; both integers
                must be from 1 to 65535
            loops: playback count from 0 to 4294967295; 0 loops forever
            skip_first: whether the first input is a static fallback outside
                playback; requires at least two inputs and ignores the fallback delay
        Raises:
            TypeError: if settings have unsupported types
            ValueError: if timing, loop count, or output suffix is invalid
            OSError: if the destination exists and is not a file
        """
        self.output_path = val_output_path(output_path, exist_ok=True, create=False)
        """Path to the completed PNG or APNG file."""
        if self.output_path.suffix.lower() not in {".png", ".apng"}:
            raise ValueError("Output must have a .png or .apng suffix")
        duration = _get_delay(delay)
        self.delay = (duration.numerator, duration.denominator)
        """Default frame delay numerator and denominator, in seconds."""
        self.loops = _validate_integer("loops", loops, 0, 4294967295)
        """Playback count, with zero denoting infinite looping."""
        if not isinstance(skip_first, bool):
            raise TypeError("skip_first must be a boolean")
        self.skip_first = skip_first
        """Whether the first input is a static fallback outside playback."""
        self._stack = ExitStack()
        self._assembler: APNGAsmBinder | None = None
        self._previous_pixels: NDArray[np.uint8] | None = None
        self._duration = Fraction(0)
        self._frame_count = 0
        self._closed = False
        self._failed = False

    def __call__(self, input_obj: PipeImage, *, delay: tuple[int, int] | None = None):
        """Snapshot one image with the default or an explicit frame delay.

        Arguments:
            input_obj: static image to append in arrival order
            delay: optional (numerator, denominator) overriding this frame's timing
        Raises:
            TypeError: if delay components are not integers
            ValueError: if the context is inactive or failed, the image is animated,
                dimensions differ or are zero, or a frame delay cannot be encoded
            OSError: if the input cannot be read
        """
        if self._assembler is None or self._closed:
            raise ValueError("APNG terminus requires an active context")
        if self._failed:
            raise ValueError("Cannot append to a failed APNG terminus")
        try:
            duration = _get_delay(self.delay if delay is None else delay)
            # PipeImage palette conversion can discard animation metadata
            if input_obj.path is not None:
                with Image.open(input_obj.path) as file_image:
                    if getattr(file_image, "is_animated", False):
                        raise ValueError("APNG input frames must be static images")
            image = input_obj.image
            if getattr(image, "is_animated", False):
                raise ValueError("APNG input frames must be static images")
            if image.width == 0 or image.height == 0:
                raise ValueError("Frame dimensions must be nonzero")
            pixels = np.array(image.convert("RGBA"), dtype=np.uint8, order="C")
            pixels[pixels[:, :, 3] == 0, :3] = 0
            if self._previous_pixels is not None:
                if pixels.shape != self._previous_pixels.shape:
                    raise ValueError("APNG frame dimensions must have the same size")
                if (not self.skip_first or self._frame_count != 1) and np.array_equal(
                    pixels, self._previous_pixels
                ):
                    self._duration += duration
                    self._frame_count += 1
                    return
                _add_frame(self._assembler, self._previous_pixels, self._duration)
            self._previous_pixels = pixels
            self._duration = duration
            self._frame_count += 1
        except BaseException:
            self._failed = True
            raise

    def __enter__(self) -> Self:
        """Create the output directory and acquire native frame storage.

        Returns:
            this active terminus
        Raises:
            ValueError: if this terminus is already active or closed
            OSError: if the output directory cannot be created
        """
        if self._assembler is not None or self._closed:
            raise ValueError("Cannot reenter an active or closed APNG terminus")
        try:
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            self._assembler = self._stack.enter_context(APNGAsmBinder())
            self._assembler.set_loops(self.loops)
            self._assembler.set_skip_first(self.skip_first)
        except BaseException:
            self._closed = True
            self._assembler = None
            self._stack.close()
            raise
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ):
        """Publish the completed animation or discard it after any failure.

        Arguments:
            exc_type: active exception type, if any
            exc_value: active exception, if any
            traceback: active traceback, if any
        Raises:
            ValueError: if the context is inactive, a frame failed, too few frames
                were collected, or the final combined delay cannot be encoded
            OSError: if writing or replacing the destination fails
            PipeScalerError: if native assembly, decoding, or Windows staging fails
        """
        if self._assembler is None or self._closed:
            raise ValueError("APNG terminus requires an active context")
        self._closed = True
        try:
            with self._stack:
                if exc_type is not None:
                    return
                if self._failed:
                    raise ValueError("Cannot publish APNG after a failed frame")
                if self._frame_count < (2 if self.skip_first else 1):
                    raise ValueError(
                        "At least one animation frame is required after skip_first"
                    )
                if self._previous_pixels is not None:
                    _add_frame(self._assembler, self._previous_pixels, self._duration)
                with get_temp_file_path(
                    ".png", parent_dir_path=self.output_path.parent
                ) as temp_path:
                    _encode(self._assembler, temp_path)
                    try:
                        with Image.open(temp_path) as image:
                            for index in range(image.n_frames):
                                image.seek(index)
                                image.load()
                    except OSError as exc:
                        raise PipeScalerError(
                            "libapngasm produced an invalid PNG"
                        ) from exc
                    self._stack.close()
                    temp_path.replace(self.output_path)
        finally:
            self._assembler = None
            self._previous_pixels = None

    def __repr__(self) -> str:
        """Describe the destination and animation settings.

        Returns:
            reconstructible terminus configuration
        """
        return (
            f"{self.__class__.__name__}(output_path={str(self.output_path)!r}, "
            f"delay={self.delay!r}, loops={self.loops!r}, "
            f"skip_first={self.skip_first!r})"
        )


def _add_frame(assembler: APNGAsmBinder, pixels: NDArray[np.uint8], duration: Fraction):
    """Add one distinct frame with an exactly representable delay.

    Arguments:
        assembler: native assembler receiving the frame
        pixels: canonical RGBA pixels
        duration: exact combined delay for the duplicate run
    Raises:
        ValueError: if the reduced delay exceeds APNG's 16-bit timing fields
    """
    if duration.numerator > 65535 or duration.denominator > 65535:
        raise ValueError(
            "Combined duplicate-frame delay must fit APNG's 16-bit timing fields"
        )
    assembler.add_frame_from_numpy(
        pixels, delay_num=duration.numerator, delay_den=duration.denominator
    )


def _encode(assembler: APNGAsmBinder, output_path: Path):
    """Encode through a native-compatible temporary path and copy the result.

    Arguments:
        assembler: configured native assembler with validated frames
        output_path: adjacent temporary destination used for atomic publication
    Raises:
        OSError: if temporary encoding or copying the result fails
        PipeScalerError: if native assembly fails, produces no file, or the
            Windows fallback cannot create a temporary file in the current cwd
    """
    native_dir_path = Path(gettempdir())
    use_relative_path = os_name == "nt" and not str(native_dir_path).isascii()
    if use_relative_path:
        native_dir_path = Path.cwd()
    with ExitStack() as temporary_files:
        try:
            native_path = temporary_files.enter_context(
                get_temp_file_path(".png", parent_dir_path=native_dir_path)
            )
        except PermissionError as exc:
            if use_relative_path:
                raise PipeScalerError(
                    "Windows APNG encoding with a non-ASCII temporary directory "
                    "requires a writable current working directory"
                ) from exc
            raise
        if use_relative_path:
            assembly_path = native_path.name
        else:
            assembly_path = str(native_path)
        try:
            assembled = assembler.assemble(assembly_path)
        except RuntimeError as exc:
            raise PipeScalerError("libapngasm assembly failed") from exc
        if not assembled or not native_path.is_file():
            raise PipeScalerError("libapngasm could not assemble the output")
        copyfile(native_path, output_path)


def _get_delay(delay: tuple[int, int]) -> Fraction:
    """Validate an exact frame delay before unsigned native conversion.

    Arguments:
        delay: frame delay numerator and denominator
    Returns:
        reduced positive duration in seconds
    Raises:
        TypeError: if delay components are not integers
        ValueError: if the pair or its 16-bit component ranges are invalid
    """
    numerator, denominator = delay
    return Fraction(
        _validate_integer("delay numerator", numerator, 1, 65535),
        _validate_integer("delay denominator", denominator, 1, 65535),
    )


def _validate_integer(name: str, value: int, minimum: int, maximum: int) -> int:
    """Validate an integer without truncation or unsigned native overflow.

    Arguments:
        name: setting name used in diagnostics
        value: integer to validate
        minimum: inclusive lower bound
        maximum: inclusive upper bound
    Returns:
        validated integer
    Raises:
        TypeError: if the value is not an integer or is a boolean
        ValueError: if the value is outside the inclusive bounds
    """
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{name} must be an integer")
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be from {minimum} to {maximum}")
    return value
