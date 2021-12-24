#!/usr/bin/env python
#   pipescaler/splitter/normal_splitter.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Splits a normal map image into separate x, y, and z images"""
from __future__ import annotations

from logging import info
from typing import Any, Dict, List

import numpy as np
from PIL import Image

from pipescaler.core import Splitter, validate_image


class NormalSplitter(Splitter):
    """Splits a normal map image into separate x, y, and z images."""

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
        self.split(infile=infile, **outfiles)
        return outfiles

    def split(self, infile: str, x: str, y: str, z: str) -> None:
        """
        Split a normal map image into separate x, y, and z images

        Args:
            infile: Input file
            x: X output file
            y: Y output file
            z: Z output file
        """
        # Read image
        input_image = validate_image(infile, "RGB")

        # Split image
        input_array = np.array(input_image)

        x_array = input_array[:, :, 0]
        y_array = input_array[:, :, 1]
        z_array = (input_array[:, :, 2].astype(float) - 128) * 2
        z_array = np.clip(z_array, 0, 255).astype(np.uint8)

        x_image = Image.fromarray(x_array)
        y_image = Image.fromarray(y_array)
        z_image = Image.fromarray(z_array)

        # Write images
        x_image.save(x)
        info(f"'{self}: '{x}' saved")
        y_image.save(y)
        info(f"'{self}: '{y}' saved")
        z_image.save(z)
        info(f"'{self}: '{z}' saved")

    @property
    def outlets(self) -> List[str]:
        """Outlets that flow out of stage"""
        return ["x", "y", "z"]
