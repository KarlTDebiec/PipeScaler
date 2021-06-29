#!/usr/bin/env python
#   pipescaler/sorters/mode_sorter.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from os.path import isfile
from typing import Any, Generator, List, Optional, Union

import numpy as np
from IPython import embed
from PIL import Image

from pipescaler.common import validate_int, validate_output_path
from pipescaler.core import PipeImage, Sorter


####################################### CLASSES ########################################
class ModeSorter(Sorter):

    # region Properties

    @property
    def outlets(self):
        return ["rgba", "rgb", "l"]

    # endregion

    # region Class Methods

    @classmethod
    def process_file(cls, infile: str, verbosity: int = 1, **kwargs: Any) -> None:
        raise NotImplementedError()

    # endregion
