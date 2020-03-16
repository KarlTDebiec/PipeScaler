#!python
#   lauhseuisin/sorters/ListSorter.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
################################### MODULES ###################################
from __future__ import annotations

from typing import Any, Iterator

from IPython import embed

from lauhseuisin.sorters.Sorter import Sorter


################################### CLASSES ###################################
class ListSorter(Sorter):

    def __init__(self, downstream_pipes_for_filenames: Any,
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.downstream_pipes_by_filename = {}
        for downstream_pipe_conf in downstream_pipes_for_filenames:
            filenames = downstream_pipe_conf.get("filenames")
            downstream_pipes = downstream_pipe_conf.get("downstream_pipes")
            if isinstance(downstream_pipes, str):
                downstream_pipes = [downstream_pipes]
            if filenames is None:
                self.default_downstream_pipes = downstream_pipes
            else:
                for filename in filenames:
                    self.downstream_pipes_by_filename[
                        filename] = downstream_pipes

    def __call__(self) -> Iterator[str]:
        while True:
            infile = (yield)
            pipes = self.downstream_pipes_by_filename.get(
                self.get_original_name(infile), self.default_downstream_pipes)
            if self.pipeline.verbosity >= 2:
                print(f"{self}: {infile}")
            if pipes is not None:
                for pipe in pipes:
                    self.pipeline.pipes[pipe].send(infile)
