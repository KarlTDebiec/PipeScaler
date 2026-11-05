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

__all__ = ["ApngasmFrame", "ApngasmRunner"]

type ApngasmFrame = Path | Image.Image | NDArray[np.uint8]
"""A static image path, Pillow image, or uint8 array with RGB/RGBA channel order."""


class ApngasmRunner:
    """Assemble ordered frames without an external executable.

    Each input contributes one frame. Pillow images and static image files are
    converted to RGBA; arrays must have shape (height, width, 3 or 4). All frames
    must have the same nonzero dimensions. Inputs are not modified. Consecutive
    visually identical animation frames are combined using exact rational timing;
    their reduced total delay must fit APNG's 16-bit numerator and denominator.
    RGB values under zero alpha are discarded.
    """

    def __init__(
        self,
        *,
        delay_num: int = 100,
        delay_den: int = 1000,
        loops: int = 0,
        skip_first: bool = False,
    ):
        """Validate and store assembly settings.

        Arguments:
            delay_num: default frame delay numerator, from 1 to 65535
            delay_den: default frame delay denominator, from 1 to 65535;
                frame duration is delay_num / delay_den seconds
            loops: playback count, from 0 to 4294967295; 0 loops forever
            skip_first: whether the first frame is a static fallback excluded
                from animation playback
        Raises:
            TypeError: if timing or loop values are not integers or skip_first
                is not a boolean
            ValueError: if timing or loop values are outside the supported ranges
        """
        self.delay_num = self._validate_integer("delay_num", delay_num, 1, 65535)
        """Default frame delay numerator."""
        self.delay_den = self._validate_integer("delay_den", delay_den, 1, 65535)
        """Default frame delay denominator."""
        self.loops = self._validate_integer("loops", loops, 0, 4294967295)
        """Playback count, with zero denoting infinite looping."""
        if not isinstance(skip_first, bool):
            raise TypeError("skip_first must be a boolean")
        self.skip_first = skip_first
        """Whether the first frame is a static fallback outside the animation."""

    def __call__(
        self,
        frames: Sequence[ApngasmFrame],
        output_path: Path,
        *,
        delays: Sequence[tuple[int, int]] | None = None,
    ):
        """Assemble frames with the same contract as `run`.

        Arguments:
            frames: ordered static frame inputs
            output_path: destination PNG or APNG in an existing directory
            delays: optional numerator/denominator pair for every input frame
        """
        self.run(frames, output_path, delays=delays)

    def __repr__(self) -> str:
        """Return a reconstructible assembly configuration.

        Returns:
            constructor expression containing all assembly settings
        """
        return (
            f"{self.__class__.__name__}(delay_num={self.delay_num!r}, "
            f"delay_den={self.delay_den!r}, loops={self.loops!r}, "
            f"skip_first={self.skip_first!r})"
        )

    def run(
        self,
        frames: Sequence[ApngasmFrame],
        output_path: Path,
        *,
        delays: Sequence[tuple[int, int]] | None = None,
    ):
        """Assemble frames and replace the destination after successful encoding.

        One input produces a static PNG. With `skip_first`, at least two inputs
        are required and the first input's delay is unused. File inputs must be
        static; animated images are rejected rather than expanded implicitly.
        The output directory must already exist. An existing output is preserved
        if validation or encoding fails.

        Native encoding uses the system temporary directory. On Windows, a
        non-ASCII temporary directory instead requires a writable current working
        directory, where encoding uses an ASCII filename without changing cwd.

        Arguments:
            frames: ordered image paths, Pillow images, or uint8 RGB/RGBA arrays
            output_path: output path with a .png or .apng suffix
            delays: optional (numerator, denominator) pair for each input frame;
                both integers must be from 1 to 65535
        Raises:
            TypeError: if frame types, array dtype, or delay types are unsupported
            ValueError: if frames, dimensions, delays, or output suffix are invalid,
                including a combined duplicate-frame delay outside APNG's limits
            OSError: if reading frames or writing the output fails
            PipeScalerError: if native assembly fails or produces invalid output
        """
        if len(frames) < (2 if self.skip_first else 1):
            raise ValueError(
                "At least one animation frame is required after skip_first"
            )
        frame_delays = self._get_delays(len(frames), delays)
        output_path = Path(output_path).absolute()
        if output_path.suffix.lower() not in {".png", ".apng"}:
            raise ValueError("Output must have a .png or .apng suffix")
        if output_path.is_dir():
            raise IsADirectoryError(f"Output is a directory: {output_path}")

        with APNGAsmBinder() as assembler:
            assembler.set_loops(self.loops)
            assembler.set_skip_first(self.skip_first)
            self._add_frames(assembler, frames, frame_delays)

            with get_temp_file_path(
                ".png", parent_dir_path=output_path.parent
            ) as temp_path:
                self._assemble(assembler, temp_path)
                try:
                    with Image.open(temp_path) as image:
                        for index in range(image.n_frames):
                            image.seek(index)
                            image.load()
                except OSError as exc:
                    raise PipeScalerError("libapngasm produced an invalid PNG") from exc
                temp_path.replace(output_path)

    @classmethod
    def help_markdown(cls) -> str:
        """Describe the library integration.

        Returns:
            Markdown help with a link to the binding documentation
        """
        return (
            "Creates animated PNGs using "
            "[apngasm-python](https://apngasm-python.readthedocs.io/en/latest/)."
        )

    def _add_frames(
        self,
        assembler: APNGAsmBinder,
        frames: Sequence[ApngasmFrame],
        delays: Sequence[tuple[int, int]],
    ):
        """Combine duplicate runs exactly before native timing arithmetic.

        Arguments:
            assembler: native assembler receiving distinct animation frames
            frames: ordered static inputs, including any fallback frame
            delays: validated numerator/denominator pairs for the inputs
        Raises:
            TypeError: if a frame type or array dtype is unsupported
            ValueError: if geometry is invalid or a combined delay cannot be encoded
            OSError: if an input file cannot be read
        """
        previous_pixels: NDArray[np.uint8] | None = None
        duration = Fraction(0)
        for index, (frame, delay) in enumerate(zip(frames, delays, strict=True)):
            pixels = self._get_pixels(frame)
            if previous_pixels is not None:
                if pixels.shape != previous_pixels.shape:
                    raise ValueError(f"Frame {index} has a different size")
                if (not self.skip_first or index != 1) and np.array_equal(
                    pixels, previous_pixels
                ):
                    duration += Fraction(*delay)
                    continue
                self._add_frame(assembler, previous_pixels, duration)
            previous_pixels = pixels
            duration = Fraction(*delay)
        if previous_pixels is not None:
            self._add_frame(assembler, previous_pixels, duration)

    def _get_delays(
        self, frame_count: int, delays: Sequence[tuple[int, int]] | None
    ) -> list[tuple[int, int]]:
        """Resolve default timing or validate each explicit frame delay.

        Arguments:
            frame_count: number of input frames including any static fallback
            delays: optional per-frame numerator/denominator pairs
        Returns:
            one validated delay pair per input frame
        Raises:
            TypeError: if delay components are not integers
            ValueError: if the number of pairs or component ranges are invalid
        """
        if delays is None:
            return [(self.delay_num, self.delay_den)] * frame_count
        if len(delays) != frame_count:
            raise ValueError("delays must contain one pair for every input frame")
        return [
            (
                self._validate_integer("delay numerator", numerator, 1, 65535),
                self._validate_integer("delay denominator", denominator, 1, 65535),
            )
            for numerator, denominator in delays
        ]

    @staticmethod
    def _add_frame(
        assembler: APNGAsmBinder, pixels: NDArray[np.uint8], duration: Fraction
    ):
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

    @staticmethod
    def _assemble(assembler: APNGAsmBinder, output_path: Path):
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

    @staticmethod
    def _get_pixels(frame: ApngasmFrame) -> NDArray[np.uint8]:
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
            raise ValueError(
                "Frame arrays must have nonzero shape (height, width, 3 or 4)"
            )
        if pixels.shape[2] == 3:
            alpha = np.full((*pixels.shape[:2], 1), 255, dtype=np.uint8)
            pixels = np.concatenate((pixels, alpha), axis=2)
        else:
            # Own writable contiguous pixels before canonicalizing hidden colors
            pixels = np.array(pixels, copy=True, order="C")
        pixels[pixels[:, :, 3] == 0, :3] = 0
        # Native pixel reads ignore strides, including those retained by concatenation
        return np.ascontiguousarray(pixels)

    @staticmethod
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
