#!/usr/bin/env python
#   common/__init__.py
#
#   Copyright (C) 2017-2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""
General-purpose code not tied to a particular project.

Last updated 2020-09-10.
"""
####################################### MODULES ########################################
from pathlib import Path

###################################### VARIABLES #######################################
package_root: str = str(Path(__file__).parent.parent.absolute())

####################################### MODULES ########################################
from typing import List

from .cltool import CLTool
from .general import (
    embed_kw,
    get_ext,
    get_name,
    get_shell_type,
    input_prefill,
    load_yaml,
    temporary_filename,
    validate_float,
    validate_input_path,
    validate_int,
    validate_output_path,
    validate_type,
)

######################################### ALL ##########################################
__all__: List[str] = [
    "CLTool",
    "embed_kw",
    "get_ext",
    "get_name",
    "get_shell_type",
    "input_prefill",
    "load_yaml",
    "package_root",
    "temporary_filename",
    "validate_float",
    "validate_input_path",
    "validate_int",
    "validate_output_path",
    "validate_type",
]
