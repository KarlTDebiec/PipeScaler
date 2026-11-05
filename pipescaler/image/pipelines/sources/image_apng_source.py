#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Yields displayed frames from an animated PNG."""

from __future__ import annotations

from pathlib import Path
from types import TracebackType
from typing import Self

from PIL import Image
from PIL.PngImagePlugin import Blend, Disposal, PngImageFile

from pipescaler.common.validation import val_input_path
from pipescaler.image.core.pipelines import ImageSource, PipeImage

__all__ = ["ImageApngSource"]


class ImageApngSource(ImageSource):
    """Yields independent, full-canvas RGBA frames in playback order.

    Frames are composited with APNG blending and disposal before being yielded.
    A separate default image is skipped unless `include_default` is enabled;
    a static PNG yields one frame. Frames receive six-digit names starting at
    `000001`. Timing and loop settings belong to the output terminus and are
    not propagated through the pipeline.

    Exhaustion and decoding errors close the decoder. Call `close()` or use a
    `with` block when iteration may stop early. Yielded frames remain usable
    after the decoder closes.
    """

    def __init__(
        self,
        input_path: Path | str,
        location_path: Path | None = None,
        *,
        include_default: bool = False,
    ):
        """Open and validate the PNG decoder.

        Arguments:
            input_path: animated or static PNG file
            location_path: path relative to parent directory
            include_default: whether to yield a separate default image before
                playback frames; configure the output terminus with `skip_first`
                when retaining that image as a fallback
        Raises:
            FileNotFoundError: if the input file does not exist
            TypeError: if include_default is not a bool or the path is invalid
            ValueError: if the input is not a PNG or contains no playback frames
            OSError: if the file cannot be opened or its header cannot be decoded
        """
        self.input_path = val_input_path(input_path)
        """Absolute input PNG path."""
        self.location_path = location_path
        """Path relative to parent directory."""
        if not isinstance(include_default, bool):
            raise TypeError("include_default must be a bool.")
        self.include_default = include_default
        """Whether a separate default image is yielded before playback frames."""
        self.index = 0
        """Number of successfully yielded frames."""
        self._canvas: Image.Image | None = None
        image = Image.open(self.input_path)
        try:
            if not isinstance(image, PngImageFile):
                raise ValueError(f"Input '{self.input_path}' is not a PNG.")
            self._start_frame = 0
            if image.info.get("default_image") and not include_default:
                self._start_frame = 1
            self.length = image.n_frames - self._start_frame
            """Number of frames to yield, excluding any skipped default image."""
            if self.length < 1:
                raise ValueError(f"PNG '{self.input_path}' has no playback frames.")
        except BaseException:
            image.close()
            raise
        self._image: PngImageFile | None = image

    def __enter__(self) -> Self:
        """Return this source for deterministic decoder cleanup.

        Returns:
            this open source
        Raises:
            ValueError: if this source is already closed
        """
        if self._image is None:
            raise ValueError("Cannot enter a closed APNG source.")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ):
        """Close the decoder without suppressing exceptions.

        Arguments:
            exc_type: active exception type, if any
            exc_value: active exception, if any
            traceback: active traceback, if any
        """
        self.close()

    def __next__(self) -> PipeImage:
        """Decode and detach the next displayed frame.

        Returns:
            next full-canvas RGBA frame
        Raises:
            StopIteration: when closed or all frames have been yielded
            OSError: if a frame cannot be decoded
        """
        if self._image is None:
            raise StopIteration
        try:
            self._image.seek(self._start_frame + self.index)
            image, self._canvas = self._decode_frame(self._image, self._canvas)
            location_path = Path(
                f"{self.input_path.stem}_{self.input_path.suffix.lstrip('.')}"
            )
            if self.location_path is not None:
                location_path = self.location_path / location_path
            obj = PipeImage(
                image=image,
                name=f"{self.index + 1:06d}",
                location_path=location_path,
            )
        except (EOFError, OSError, SyntaxError) as exc:
            self.close()
            raise OSError(
                f"Cannot decode APNG frame {self.index + 1} of "
                f"{self.length} in '{self.input_path}'."
            ) from exc
        except BaseException:
            self.close()
            raise
        self.index += 1
        if self.index == self.length:
            self.close()
        return obj

    def __repr__(self) -> str:
        """Reconstructible representation.

        Returns:
            string representation of this source's configuration
        """
        location_path = repr(self.location_path)
        if self.location_path is not None:
            location_path = f"Path({str(self.location_path)!r})"
        return (
            f"{self.__class__.__name__}(input_path=Path({str(self.input_path)!r}), "
            f"location_path={location_path}, include_default={self.include_default!r})"
        )

    def close(self):
        """Release the decoder and permanently stop iteration."""
        image = self._image
        self._image = None
        self._canvas = None
        if image is not None:
            image.close()

    @staticmethod
    def _decode_frame(
        decoder: PngImageFile, canvas: Image.Image | None
    ) -> tuple[Image.Image, Image.Image]:
        """Composite a decoded frame and prepare the canvas for its successor.

        Pillow's masked-paste OVER blending also interpolates alpha, producing
        incorrect transparency. Decode the frame with SOURCE blending, then
        compose its rectangle with straight-alpha compositing instead.

        Arguments:
            decoder: PNG decoder positioned at the next frame
            canvas: disposed RGBA canvas from the preceding frame, if any
        Returns:
            detached displayed frame and canvas after disposal
        """
        if canvas is None:
            canvas = Image.new("RGBA", decoder.size)
        bbox = decoder.info.get("bbox", (0, 0, *decoder.size))
        blend = decoder.info.get("blend", Blend.OP_SOURCE)
        disposal = decoder.info.get("disposal", Disposal.OP_NONE)
        previous = canvas
        if disposal == Disposal.OP_PREVIOUS:
            previous = canvas.copy()

        # Keep Pillow's decoder from compositing before the raw rectangle is copied
        setattr(decoder, "blend_op", Blend.OP_SOURCE)
        patch = decoder.convert("RGBA").crop(bbox)
        if blend == Blend.OP_OVER:
            canvas.alpha_composite(patch, dest=bbox[:2])
        else:
            canvas.paste(patch, bbox)
        frame = canvas.copy()
        if disposal == Disposal.OP_BACKGROUND:
            canvas.paste((0, 0, 0, 0), bbox)
        elif disposal == Disposal.OP_PREVIOUS:
            canvas = previous
        if decoder.info.get("default_image") and decoder.tell() == 0:
            canvas = Image.new("RGBA", decoder.size)
        return frame, canvas
