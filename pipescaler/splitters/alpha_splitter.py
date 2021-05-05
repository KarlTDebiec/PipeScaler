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

from typing import List, Optional

import numpy as np
from PIL import Image

from pipescaler.core import Splitter


####################################### CLASSES ########################################
class AlphaSplitter(Splitter):

    # region Properties

    @property
    def outlets(self) -> Optional[List[str]]:
        return ["rgb", "a"]

    # endregion

    # region Methods

    def process(self, inlet=None, verbosity=1):
        if inlet.mode == "RGBA":
            return (
                Image.fromarray(np.array(inlet)[:, :, 3]),
                Image.fromarray(np.array(inlet)[:, :, 1]),
            )
        else:
            raise ValueError()

    # endregion
