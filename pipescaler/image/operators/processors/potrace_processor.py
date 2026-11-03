#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Traces image using potrace and re-rasterizes, optionally resizing."""

from __future__ import annotations

from typing import Literal

import numpy as np
from PIL import Image, ImageOps
from reportlab.graphics.renderPM import drawToPIL
from reportlab.graphics.shapes import Drawing

from pipescaler.common.validation import val_float, val_int
from pipescaler.image.core.operators import ImageProcessor
from pipescaler.image.core.typing import ImageMode
from pipescaler.image.core.validation import validate_image_and_convert_mode
from pipescaler.image.utilities.potrace import trace_bitmap

__all__ = ["PotraceProcessor"]


class PotraceProcessor(ImageProcessor):
    """Traces image using potrace and re-rasterizes, optionally resizing.

    Re-rasterized output is always mode `L`, including antialiased gray pixels.

    See [Potrace](http://potrace.sourceforge.net/).
    """

    def __init__(  # noqa: PLR0913
        self,
        *,
        blacklevel: float = 0.3,
        turdsize: int = 2,
        turnpolicy: Literal[
            "black", "white", "left", "right", "minority", "majority", "random"
        ] = "minority",
        alphamax: float = 1.34,
        opticurve: bool = True,
        opttolerance: float = 0.2,
        invert: bool = False,
        scale: float = 1.0,
    ):
        """Validate and store native tracing settings.

        Arguments:
            blacklevel: inclusive grayscale cutoff in [0, 1] for foreground pixels
            turdsize: maximum area of speckles to remove, in input pixels
            turnpolicy: policy for resolving ambiguous diagonal connections
            alphamax: corner threshold; zero preserves corners, above 4/3 smooths all
            opticurve: whether to combine adjacent cubic curves
            opttolerance: curve optimization tolerance in input pixels
            invert: whether to invert both the input and re-rasterized output
            scale: positive output scale; dimensions are truncated to whole pixels
        Raises:
            ValueError: if settings are outside their supported ranges or not finite
        """
        super().__init__()
        self.blacklevel = val_float(blacklevel, min_value=0, max_value=1, finite=True)
        """Normalized grayscale cutoff for black foreground."""
        self.turdsize = val_int(turdsize, min_value=0, max_value=2**31 - 1)
        """Maximum speckle area removed from the trace."""
        self.turnpolicy = turnpolicy
        """Policy for decomposing ambiguous diagonal connections."""
        self.alphamax = val_float(alphamax, min_value=0, finite=True)
        """Threshold for smoothing corners."""
        self.opticurve = opticurve
        """Whether to combine adjacent cubic segments."""
        self.opttolerance = val_float(opttolerance, min_value=0, finite=True)
        """Curve optimization tolerance in input pixels."""
        self.invert = invert
        """Whether to invert input and output polarity."""
        self.scale = val_float(scale, min_value=0, min_exclusive=True, finite=True)
        """Output scale relative to input dimensions."""
        if self.turnpolicy not in (
            "black",
            "white",
            "left",
            "right",
            "minority",
            "majority",
            "random",
        ):
            raise ValueError(f"Unknown Potrace turn policy: {turnpolicy!r}")

    def __call__(self, input_image: Image.Image) -> Image.Image:
        """Trace and rasterize entirely in memory, retaining antialiased gray pixels.

        Arguments:
            input_image: binary or grayscale image, including grayscale palettes
        Returns:
            scaled grayscale image in mode `L`
        Raises:
            ValueError: if an output dimension rounds down to zero
            OSError: if libpotrace is unavailable
            MemoryError: if native tracing fails
        """
        input_image, _ = validate_image_and_convert_mode(
            input_image, self.inputs()["input"], "L"
        )
        width, height = input_image.size
        output_size = (int(width * self.scale), int(height * self.scale))
        if min(output_size) < 1:
            raise ValueError("Scaled output dimensions must be at least one pixel")
        if self.invert:
            input_image = ImageOps.invert(input_image)
        bitmap = np.asarray(input_image) <= self.blacklevel * 255
        policies = ("black", "white", "left", "right", "minority", "majority", "random")
        path = trace_bitmap(
            bitmap,
            turdsize=self.turdsize,
            turnpolicy=policies.index(self.turnpolicy),
            alphamax=self.alphamax,
            opticurve=self.opticurve,
            opttolerance=self.opttolerance,
        )
        drawing = Drawing(*output_size)
        drawing.add(path)
        drawing.scale(self.scale, self.scale)
        output_image = drawToPIL(drawing, bg=0xFFFFFF).convert("L")
        if self.invert:
            output_image = ImageOps.invert(output_image)
        return output_image

    def __repr__(self) -> str:
        """Return a reconstructible representation of all tracing settings.

        Returns:
            constructor expression with typed settings
        """
        return (
            f"{self.__class__.__name__}(blacklevel={self.blacklevel!r}, "
            f"turdsize={self.turdsize!r}, turnpolicy={self.turnpolicy!r}, "
            f"alphamax={self.alphamax!r}, opticurve={self.opticurve!r}, "
            f"opttolerance={self.opttolerance!r}, invert={self.invert!r}, "
            f"scale={self.scale!r})"
        )

    @classmethod
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links.

        Returns:
            markdown help describing this component
        """
        return (
            "Traces image using [Potrace](http://potrace.sourceforge.net/) and "
            "re-rasterizes, optionally resizing."
        )

    @classmethod
    def inputs(cls) -> dict[str, tuple[ImageMode, ...]]:
        """Inputs to this operator.

        Returns:
            mapping of input names to their supported image modes
        """
        return {
            "input": ("1", "L"),
        }

    @classmethod
    def outputs(cls) -> dict[str, tuple[ImageMode, ...]]:
        """Outputs of this operator.

        Returns:
            mapping of output names to their supported image modes
        """
        return {
            "output": ("L",),
        }
