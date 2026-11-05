#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Assemble animated PNGs using the bundled libapngasm bindings."""

from __future__ import annotations

from collections.abc import Sequence
from contextlib import ExitStack
from fractions import Fraction
from os import name as os_name
from pathlib import Path
from shutil import copyfile
from tempfile import gettempdir

import numpy as np
from apngasm_python.apngasm import APNGAsmBinder
from numpy.typing import NDArray
from PIL import Image

from pipescaler.common.file import get_temp_file_path
from pipescaler.core.exceptions import PipeScalerError

__all__ = ["ApngFrame", "assemble_apng"]

type ApngFrame = Path | Image.Image | NDArray[np.uint8]
"""A static image path, Pillow image, or uint8 array in RGB/RGBA channel order."""


def assemble_apng(
    frames: Sequence[ApngFrame],
    output_path: Path,
    *,
    delays: Sequence[tuple[int, int]] | None = None,
    loops: int = 0,
    skip_first: bool = False,
):
    """Assemble ordered frames into a PNG using libapngasm.

    All frames must have the same nonzero dimensions. Static image paths and
    Pillow images are converted to RGBA; arrays must have shape (height, width,
    3 or 4) and dtype uint8. Inputs are not modified. Consecutive visually identical
    animation frames combine using exact timing; their reduced total delay must
    fit APNG's 16-bit numerator and denominator. Hidden RGB under zero alpha is
    discarded. One distinct animation frame without a fallback produces a static PNG.

    The output directory must exist. The destination is replaced only after
    successful encoding and decoding. Native encoding uses the system temporary
    directory. On Windows, a non-ASCII temporary directory instead requires a
    writable current working directory, where encoding uses an ASCII filename
    without changing cwd.

    Arguments:
        frames: ordered static paths, Pillow images, or uint8 RGB/RGBA arrays
        output_path: destination with a .png or .apng suffix
        delays: optional (numerator, denominator) pair for each input frame, in
            seconds; both integers must be from 1 to 65535; defaults to 1/10 second
        loops: playback count from 0 to 4294967295; 0 loops forever
        skip_first: whether the first frame is a static fallback outside playback;
            requires at least two inputs, and the fallback's delay is unused
    Raises:
        TypeError: if frame types, array dtype, or setting types are unsupported
        ValueError: if frames, dimensions, delays, loop count, or output suffix are
            invalid, including a combined duplicate-frame delay outside APNG's limits
        OSError: if reading inputs or writing the output fails
        PipeScalerError: if native assembly, decoding, or Windows staging fails
    """
    loops = _validate_integer("loops", loops, 0, 4294967295)
    if not isinstance(skip_first, bool):
        raise TypeError("skip_first must be a boolean")
    if len(frames) < (2 if skip_first else 1):
        raise ValueError("At least one animation frame is required after skip_first")
    if delays is None:
        frame_delays = [(1, 10)] * len(frames)
    else:
        if len(delays) != len(frames):
            raise ValueError("delays must contain one pair for every input frame")
        frame_delays = [
            (
                _validate_integer("delay numerator", numerator, 1, 65535),
                _validate_integer("delay denominator", denominator, 1, 65535),
            )
            for numerator, denominator in delays
        ]
    output_path = Path(output_path).absolute()
    if output_path.suffix.lower() not in {".png", ".apng"}:
        raise ValueError("Output must have a .png or .apng suffix")
    if output_path.is_dir():
        raise IsADirectoryError(f"Output is a directory: {output_path}")

    with APNGAsmBinder() as assembler:
        assembler.set_loops(loops)
        assembler.set_skip_first(skip_first)
        _add_frames(assembler, frames, frame_delays, skip_first=skip_first)
        with get_temp_file_path(
            ".png", parent_dir_path=output_path.parent
        ) as temp_path:
            _encode(assembler, temp_path)
            try:
                with Image.open(temp_path) as image:
                    for index in range(image.n_frames):
                        image.seek(index)
                        image.load()
            except OSError as exc:
                raise PipeScalerError("libapngasm produced an invalid PNG") from exc
            temp_path.replace(output_path)


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


def _add_frames(
    assembler: APNGAsmBinder,
    frames: Sequence[ApngFrame],
    delays: Sequence[tuple[int, int]],
    *,
    skip_first: bool,
):
    """Combine duplicate runs exactly before native timing arithmetic.

    Arguments:
        assembler: native assembler receiving distinct animation frames
        frames: ordered static inputs, including any fallback frame
        delays: validated numerator/denominator pairs for the inputs
        skip_first: whether to keep the fallback separate from the first playback frame
    Raises:
        TypeError: if a frame type or array dtype is unsupported
        ValueError: if geometry is invalid or a combined delay cannot be encoded
        OSError: if an input file cannot be read
    """
    previous_pixels: NDArray[np.uint8] | None = None
    duration = Fraction(0)
    for index, (frame, delay) in enumerate(zip(frames, delays, strict=True)):
        pixels = _get_pixels(frame)
        if previous_pixels is not None:
            if pixels.shape != previous_pixels.shape:
                raise ValueError(f"Frame {index} has a different size")
            if (not skip_first or index != 1) and np.array_equal(
                pixels, previous_pixels
            ):
                duration += Fraction(*delay)
                continue
            _add_frame(assembler, previous_pixels, duration)
        previous_pixels = pixels
        duration = Fraction(*delay)
    if previous_pixels is not None:
        _add_frame(assembler, previous_pixels, duration)


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
        # A relative ASCII filename also works when the Windows cwd is Unicode
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


def _get_pixels(frame: ApngFrame) -> NDArray[np.uint8]:
    """Read and validate one frame before passing its memory to native code.

    Arguments:
        frame: static image path, Pillow image, or uint8 RGB/RGBA array
    Returns:
        owned writable contiguous RGBA pixels, with zero RGB under zero alpha
    Raises:
        TypeError: if the frame type or array dtype is unsupported
        ValueError: if the image is animated or its dimensions are invalid
        OSError: if a frame file cannot be read
    """
    if isinstance(frame, Path):
        with Image.open(frame) as image:
            if getattr(image, "is_animated", False):
                raise ValueError(f"Frame file must be static: {frame}")
            pixels = np.array(image.convert("RGBA"))
    elif isinstance(frame, Image.Image):
        if getattr(frame, "is_animated", False):
            raise ValueError("Pillow frames must be static images")
        pixels = np.array(frame.convert("RGBA"))
    elif isinstance(frame, np.ndarray):
        pixels = frame
    else:
        raise TypeError("Frames must be Paths, Pillow images, or NumPy arrays")
    if pixels.dtype != np.uint8:
        raise TypeError("Frame arrays must have dtype uint8")
    if (
        pixels.ndim != 3
        or pixels.shape[2] not in {3, 4}
        or pixels.shape[0] == 0
        or pixels.shape[1] == 0
    ):
        raise ValueError("Frame arrays must have nonzero shape (height, width, 3 or 4)")
    if pixels.shape[2] == 3:
        alpha = np.full((*pixels.shape[:2], 1), 255, dtype=np.uint8)
        pixels = np.concatenate((pixels, alpha), axis=2)
    else:
        # Own writable contiguous pixels before canonicalizing hidden colors
        pixels = np.array(pixels, copy=True, order="C")
    pixels[pixels[:, :, 3] == 0, :3] = 0
    # Native pixel reads ignore strides, including those retained by concatenation
    return np.ascontiguousarray(pixels)


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
