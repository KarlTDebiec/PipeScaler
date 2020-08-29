#!/usr/bin/env python
#   pipescaler/sorters/list_sorter.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from os.path import expandvars
from typing import Any, Generator

import yaml

from pipescaler.sorters.sorter import Sorter


####################################### CLASSES ########################################
class ListSorter(Sorter):

    # region Builtins

    def __init__(self, downstream_pipes_for_filenames: Any, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.downstream_pipes_by_filename = {}
        for name, conf in downstream_pipes_for_filenames.items():
            filenames = conf.get("filenames")
            if isinstance(filenames, str):
                with open(expandvars(filenames), "r") as f:
                    filenames = yaml.load(f, Loader=yaml.SafeLoader)
            if filenames is None:
                filenames = []
            downstream_pipes = conf.get("downstream_pipes")
            if isinstance(downstream_pipes, str):
                downstream_pipes = [downstream_pipes]
            if name == "default":
                self.default_downstream_pipes = downstream_pipes
            else:
                for filename in filenames:
                    self.downstream_pipes_by_filename[filename] = downstream_pipes

    def __call__(self) -> Generator[str, str, None]:
        while True:
            infile = yield  # type: ignore
            pipes = self.downstream_pipes_by_filename.get(
                self.get_original_name(infile), self.default_downstream_pipes
            )
            if self.pipeline.verbosity >= 2:
                print(f"{self}: {infile}")
            if pipes is not None:
                for pipe in pipes:
                    self.pipeline.pipes[pipe].send(infile)

    # endregion
