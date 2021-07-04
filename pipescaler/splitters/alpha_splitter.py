#!/usr/bin/env python
#   pipescaler/splitter/alpha_splitter.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from logging import info
from typing import Any, Dict

import numpy as np
from PIL import Image

from pipescaler.core import Splitter


####################################### CLASSES ########################################
class AlphaSplitter(Splitter):

    # region Builtins

    def __call__(self, infile: str, **kwargs: Any) -> Dict[str, str]:
        outfiles = {k: kwargs.get(k) for k in self.outlets}

        # Read image
        rgba = Image.open(infile)
        if rgba.mode != "RGBA":
            raise ValueError()

        # Split images
        rgb = Image.fromarray(np.array(rgba)[:, :, :3])
        a = Image.fromarray(np.array(rgba)[:, :, 3])

        # Write images
        rgb.save(outfiles["rgb"])
        info(f"{self}: '{outfiles['rgb']}' saved")
        a.save(outfiles["a"])
        info(f"{self}: '{outfiles['a']}' saved")

        return outfiles

    # endregion

    # region Properties

    @property
    def outlets(self):
        return ["rgb", "a"]

    # endregion
