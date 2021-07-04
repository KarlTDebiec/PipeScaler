#!/usr/bin/env python
#   pipescaler/splitter/normal_splitter.py
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
class NormalSplitter(Splitter):

    # region Builtins

    def __call__(self, infile: str, **kwargs: Any) -> Dict[str, str]:
        outfiles = {k: kwargs.get(k) for k in self.outlets}

        # Read image
        rgb = Image.open(infile)

        # Split image
        r = Image.fromarray(np.array(rgb)[:, :, 0])
        g = Image.fromarray(np.array(rgb)[:, :, 1])
        b = Image.fromarray(np.array(rgb)[:, :, 2])
        # TODO: Should this spread out blue channel from 128-255 to 0-255?

        # Write images
        r.save(outfiles["r"])
        info(f"'{self}: '{outfiles['r']}' saved")
        g.save(outfiles["g"])
        info(f"'{self}: '{outfiles['g']}' saved")
        b.save(outfiles["b"])
        info(f"'{self}: '{outfiles['b']}' saved")

        return outfiles

    # endregion

    # region Properties

    @property
    def outlets(self):
        return ["r", "g", "b"]

    # endregion
