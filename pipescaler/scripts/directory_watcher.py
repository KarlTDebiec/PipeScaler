#!/usr/bin/env python
#   pipescaler/scripts/directory_watcher.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
""""""
####################################### MODULES ########################################
from __future__ import annotations

import re
from argparse import ArgumentParser
from typing import Any, List, Union

import yaml

from pipescaler.common import CLTool, validate_input_path
from pipescaler.core.pipeline import Pipeline


####################################### CLASSES ########################################
class DirectoryWatcher(CLTool):

    # region Builtins

    def __init__(self, directory: str, regex: str, **kwargs: Any) -> None:
        """
        Initializes.

        Args:
            conf_file (str): file from which to load configuration
        """
        super().__init__(**kwargs)

        # Store configuration
        self.regex = re.compile(regex)

    @abstractmethod
    def __call__(self, **kwargs) -> Any:
        """Perform operations."""
        raise NotImplementedError()

    # endregion


######################################### MAIN #########################################
if __name__ == "__main__":
    DirectoryWatcher.main()
