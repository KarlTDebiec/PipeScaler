#!/usr/bin/env python
#   pipescaler/splitter/alpha_splitter.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Splits image with transparency into separate alpha and color images"""
from __future__ import annotations

from logging import info
from typing import Any, Dict, List

import numpy as np
from PIL import Image

from pipescaler.core import Splitter, validate_image


class AlphaSplitter(Splitter):
    """Splits image with transparency into separate alpha and color images."""

    def __call__(self, infile: str, **kwargs: Any) -> Dict[str, str]:
        """
        Split image

        Args:
            infile: Input file
            **kwargs: Additional keyword arguments

        Returns:
            Dict whose keys are outlet names and whose values are the paths to each
            outlet's associated outfile
        """
        outfiles = {k: kwargs.get(k) for k in self.outlets}
        self.split(infile, **outfiles)
        return outfiles

    def split(self, infile: str, color: str, alpha: str) -> None:
        """
        Split image with transparency into separate alpha and color images

        Args:
            infile: Input file
            color: Color output file
            alpha: Z output file
        """
        # Read image
        input_image = validate_image(infile, ["LA", "RGBA"])

        # Split image
        input_array = np.array(input_image)
        color_array = np.squeeze(input_array[:, :, :-1])
        alpha_array = input_array[:, :, -1]
        color_image = Image.fromarray(color_array)
        alpha_image = Image.fromarray(alpha_array)

        # Write images
        color_image.save(color)
        info(f"{self}: '{color}' saved")
        alpha_image.save(alpha)
        info(f"{self}: '{alpha}' saved")

    @property
    def outlets(self) -> List[str]:
        """Outlets that flow out of stage"""
        return ["color", "alpha"]
