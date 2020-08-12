#!/usr/bin/env python
#   pipescaler/__init__.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
################################### MODULES ###################################
from argparse import ArgumentError
from os import R_OK, access
from os.path import exists, expandvars, isdir, isfile
from pathlib import Path

################################## VARIABLES ##################################
package_root: str = str(Path(__file__).parent.absolute())
