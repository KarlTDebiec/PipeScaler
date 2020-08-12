#!/usr/bin/env python
#   common/__init__.py
#
#   Copyright (C) 2017-2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
""""""
################################### MODULES ###################################
from pathlib import Path

################################## VARIABLES ##################################
package_root: str = str(Path(__file__).parent.parent.absolute())

################################### MODULES ###################################
from typing import List

from .cltool import CLTool
from .general import embed_kw, get_shell_type, input_prefill, todo

##################################### ALL #####################################
__all__: List[str] = [
    "CLTool",
    "embed_kw",
    "get_shell_type",
    "input_prefill",
    "package_root",
    "todo"
]
