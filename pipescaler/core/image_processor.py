#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Base class for processors that perform their processing within python."""
from __future__ import annotations

from abc import ABC, abstractmethod
from logging import info

from PIL import Image

from pipescaler.core.processor import Processor
from pipescaler.core.validation import validate_image


class ImageProcessor(Processor, ABC):
    """Base class for processors that perform their processing within python."""

    def __call__(self, infile: str, outfile: str) -> None:
        """
        Read image from infile, process it, and save to outfile

        Arguments:
            infile: Input file path
            outfile: Output file path
        """
        input_image = validate_image(infile, self.supported_input_modes)

        output_image = self.process(input_image)

        output_image.save(outfile)
        info(f"{self}: '{outfile}' saved")

    @abstractmethod
    def process(self, input_image: Image.Image) -> Image.Image:
        """
        Process an image

        Arguments:
            input_image: Input image to process
        Returns:
            Processed output image
        """
        raise NotImplementedError()

    @classmethod
    @property
    def supported_input_modes(self) -> list[str]:
        """Supported modes for input image"""
        return ["1", "L", "LA", "RGB", "RGBA"]
