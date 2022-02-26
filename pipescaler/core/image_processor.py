#!/usr/bin/env python
#   pipescaler/core/image_processor.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Base class for processors that perform their processing within python"""
from __future__ import annotations

from abc import ABC, abstractmethod
from logging import info
from typing import List

from PIL import Image

from pipescaler.core.processor import Processor
from pipescaler.core.validation import validate_image


class ImageProcessor(Processor, ABC):
    """Base class for processors that perform their processing within python"""

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

    @property
    def supported_input_modes(self) -> List[str]:
        """Supported image modes for input put"""
        return ["1", "L", "LA", "RGB", "RGBA"]

    @abstractmethod
    def process(self, input_image: Image.Image) -> Image.Image:
        raise NotImplementedError()
