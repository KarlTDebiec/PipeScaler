#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Functions for interacting with files."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from pipescaler.common import validate_input_file


def read_yaml(path: Path) -> Any:
    """Read a yaml file and returns the contents.

    Arguments:
        path: Path to input file
    Returns:
        Data structure loaded from yaml
    """
    with open(validate_input_file(path), "r", encoding="utf8") as yaml_file:
        return yaml.load(yaml_file, Loader=yaml.SafeLoader)
