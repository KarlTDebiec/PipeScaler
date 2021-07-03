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

from typing import Any, Dict

import numpy as np
from PIL import Image

from pipescaler.core import Splitter


####################################### CLASSES ########################################
class AlphaSplitter(Splitter):

    # region Builtins

    def __call__(
        self, infile: str, verbosity: int = 1, **kwargs: Any
    ) -> Dict[str, str]:
        outfiles = {k: kwargs.get(k) for k in self.outlets}

        rgba = Image.open(infile)
        if verbosity >= 1:
            print(f"Saving rgb to '{outfiles['rgb']}'")
        Image.fromarray(np.array(rgba)[:, :, :3]).save(outfiles["rgb"])
        if verbosity >= 1:
            print(f"Saving alpha to '{outfiles['a']}'")
        Image.fromarray(np.array(rgba)[:, :, 3]).save(outfiles["a"])

        return outfiles

    # endregion

    # region Properties

    @property
    def outlets(self):
        return ["rgb", "a"]

    # endregion
