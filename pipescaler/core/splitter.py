#!/usr/bin/env python
#   pipescaler/core/splitter.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Base class for splitters"""
from __future__ import annotations

from abc import ABC
from logging import info
from typing import Any, Optional

from PIL import Image

from pipescaler.core.stage import Stage
from pipescaler.core.validation import validate_image


class Splitter(Stage, ABC):
    """Base class for splitters"""

    def __init__(
        self, suffixes: Optional[dict[str, str]] = None, **kwargs: Any
    ) -> None:
        """
        Validate and store static configuration

        Arguments:
            suffixes: Suffixes to add to split outfiles
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Store configuration
        if suffixes is not None:
            self.suffixes = suffixes
        else:
            self.suffixes = {outlet: outlet for outlet in self.outlets}

    def __call__(self, infile: str, **kwargs: Any) -> dict[str, str]:
        """
        Split infile into outfiles

        Arguments:
            infile: Input file
            **kwargs: Additional keyword arguments; including one argument for each
              outlet, whose key is the name of that outlet and whose value is the path
              to the associated outfile

        Returns:
            Dict whose keys are outlet names and whose values are the paths to each
            outlet's associated outfile
        """
        input_image = validate_image(infile, self.supported_input_modes)

        output_images = self.split(input_image)

        outfiles = {k: kwargs.get(k) for k in self.outlets}
        for outlet, output_image in zip(self.outlets, output_images):
            output_image.save(outfiles[outlet])
            info(f"{self}: '{outfiles[outlet]}' saved")

        return outfiles

    @property
    def inlets(self) -> list[str]:
        """Inlets that flow into stage"""
        return ["infile"]

    @classmethod
    @property
    def supported_input_modes(self) -> list[str]:
        """Supported modes for input image"""
        return ["1", "L", "LA", "RGB", "RGBA"]

    def split(self, input_image: Image.Image) -> tuple[Image.Image, ...]:
        """
        Split an image

        Arguments:
            input_image: Input image to split
        Returns:
            Split output images
        """
        raise NotImplementedError()
