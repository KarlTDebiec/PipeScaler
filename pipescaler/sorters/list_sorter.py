#!/usr/bin/env python
#   pipescaler/sorters/list_sorter.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from logging import info
from os import listdir
from os.path import basename, dirname, isdir, splitext
from typing import Any, Dict, List

from pipescaler.common import validate_input_path
from pipescaler.core import Sorter


####################################### CLASSES ########################################
class ListSorter(Sorter):

    # region Builtins

    def __init__(self, outlets: Dict[str, List[str]], **kwargs: Any) -> None:
        super().__init__(**kwargs)

        # Store configuration
        self._outlets = list(outlets.keys())
        self._outlets_by_filename = {}

        # Organize downstream outlets
        for outlet in self.outlets:
            outlet_conf = outlets[outlet]
            if isinstance(outlet_conf, str):
                outlet_conf_dir = validate_input_path(
                    outlet_conf, directory_ok=True, file_ok=False
                )
                if isdir(outlet_conf_dir):
                    for infile in listdir(outlet_conf_dir):
                        name = splitext(basename(infile)[0])
                        self._outlets_by_filename[name] = outlet
                else:
                    raise ValueError()
            elif isinstance(outlet_conf, list):
                for name in outlet_conf:
                    self._outlets_by_filename[name] = outlet

    def __call__(self, infile: str) -> str:
        # Identify image
        name = basename(dirname(infile))

        # Sort image
        outlet = self.outlets_by_filename.get(name, None)
        if outlet is not None:
            info(f"{self}: '{name}' matches '{outlet}'")
        else:
            info(f"{self}: '{name}' does not match")
        return outlet

    # endregion

    # region Properties

    @property
    def outlets(self) -> List[str]:
        return self._outlets

    @property
    def outlets_by_filename(self) -> Dict[str, str]:
        return self._outlets_by_filename

    # endregion
