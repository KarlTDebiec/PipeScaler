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

from typing import Any, Dict

import numpy as np
from PIL import Image

from pipescaler.core import Splitter


####################################### CLASSES ########################################
class NormalSplitter(Splitter):

    # region Builtins

    def __call__(
        self, infile: str, verbosity: int = 1, **kwargs: Any
    ) -> Dict[str, str]:
        outfiles = {k: kwargs.get(k) for k in self.outlets}

        rgb = Image.open(infile)
        if verbosity >= 1:
            print(f"Saving r to '{outfiles['r']}'")
        Image.fromarray(np.array(rgb)[:, :, 0]).save(outfiles["r"])
        if verbosity >= 1:
            print(f"Saving g to '{outfiles['g']}'")
        Image.fromarray(np.array(rgb)[:, :, 1]).save(outfiles["g"])
        if verbosity >= 1:
            print(f"Saving b to '{outfiles['b']}'")
        Image.fromarray(np.array(rgb)[:, :, 2]).save(outfiles["b"])
        # TODO: Should this spread out blue channel from 128-255 to 0-255?

        return outfiles

    # endregion

    # region Properties

    @property
    def outlets(self):
        return ["r", "g", "b"]

    # endregion
