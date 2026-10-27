#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Matches an image's color palette to that of a reference image."""

from __future__ import annotations

from PIL import Image

from pipescaler.image.core import UnsupportedImageModeError
from pipescaler.image.core.operators import ImageMerger
from pipescaler.image.core.typing import ImageMode
from pipescaler.image.core.validation import validate_image
from pipescaler.image.utilities import PaletteMatcher

__all__ = ["PaletteMatchMerger"]


class PaletteMatchMerger(ImageMerger):
    """Matches an image's color palette to the full reference palette."""

    def __call__(self, *input_images: Image.Image) -> Image.Image:
        """Merge images.

        Arguments:
            *input_images: Input images
        Returns:
            Merged output image
        Raises:
            UnsupportedImageModeError: if an image mode is unsupported
        """
        ref_image = validate_image(input_images[0], self.inputs()["ref"])
        fit_image = validate_image(input_images[1], self.inputs()["fit"])
        if ref_image.mode != fit_image.mode:
            raise UnsupportedImageModeError(
                f"Image mode '{ref_image.mode}' of reference image does not match mode "
                f"'{fit_image.mode}' of fit image"
            )

        return PaletteMatcher.run(ref_image, fit_image)

    def __repr__(self) -> str:
        """Representation.

        Returns:
            string representation of this object
        """
        return f"{self.__class__.__name__}()"

    @classmethod
    def inputs(cls) -> dict[str, tuple[ImageMode, ...]]:
        """Inputs to this operator.

        Returns:
            mapping of input names to their supported image modes
        """
        return {
            "ref": ("L", "RGB"),
            "fit": ("L", "RGB"),
        }

    @classmethod
    def outputs(cls) -> dict[str, tuple[ImageMode, ...]]:
        """Outputs of this operator.

        Returns:
            mapping of output names to their supported image modes
        """
        return {
            "output": ("L", "RGB"),
        }
