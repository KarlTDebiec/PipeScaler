#!/usr/bin/env python
#   pipescaler/sources/directory_source.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from pipescaler.common import get_name
from pipescaler.core import Source


####################################### CLASSES ########################################
class DirectorySource(Source):

    # region Static Methods

    @staticmethod
    def sort(filename):
        return "".join([f"{ord(c):03d}" for c in filename])

    # endregion
