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

from os import listdir
from os.path import isdir
from typing import Any, Dict, Generator

from pipescaler.common import get_name, load_yaml, validate_input_path
from pipescaler.core import Sorter


####################################### CLASSES ########################################
class ListSorter(Sorter):

    # region Builtins

    def __init__(
        self, downstream_forks: Dict[str, Dict[str, Any]], **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)

        desc = f"{self.name} {self.__class__.__name__}"
        downstream_forks_by_filename = {}
        default_fork_name = None
        default_downstream_stages = None

        # Loop over forks
        for fork_name, fork_conf in downstream_forks.items():
            if fork_conf is None:
                fork_conf = {}

            # Parse file definitions for this class
            infiles = fork_conf.get("infiles")

            if infiles is None:
                if default_fork_name is not None:
                    raise ValueError(
                        "At most one configuration may omit 'infiles' "
                        "and will be used as the default fork"
                    )
                default_fork_name = fork_name
                downstream_stages = fork_conf.get("downstream_stages")
                if isinstance(downstream_stages, str):
                    downstream_stages = [downstream_stages]
                default_downstream_stages = downstream_stages
                continue

            if isinstance(infiles, str):
                infiles = [infiles]
            filenames = set()
            desc += f"\n ├─ {fork_name} ("
            for infile in infiles:
                infile = validate_input_path(infile, file_ok=True, directory_ok=True)
                desc += f"{infile}, "
                if isdir(infile):
                    filenames |= {get_name(f) for f in listdir(infile)}
                else:
                    filenames |= {get_name(f) for f in load_yaml(infile)}
            desc = f"{desc.rstrip(', ')}, {len(filenames)} filenames)"

            # Parse downstream stages for this class
            downstream_stages = fork_conf.get("downstream_stages")
            if isinstance(downstream_stages, str):
                downstream_stages = [downstream_stages]
            if downstream_stages is not None:
                if len(downstream_stages) >= 2:
                    for stage in downstream_stages:
                        desc += f"\n │   ├─ {stage}"
                desc += f"\n │   └─ {downstream_stages[-1]}"
                for filename in filenames:
                    downstream_forks_by_filename[filename] = downstream_stages
            else:
                desc += f"\n │   └─"

        # Add description for default fork
        if default_fork_name is None:
            default_fork_name = "default"
        desc += f"\n └─ {default_fork_name}"
        if default_downstream_stages is not None:
            if len(default_downstream_stages) >= 2:
                for stage in default_downstream_stages[:-1]:
                    desc += f"\n     ├─ {stage}:"
            desc += f"\n     └─ {default_downstream_stages[-1]}"
        else:
            desc += f"\n     └─"

        # Store results
        self.desc = desc
        self.downstream_forks_by_filename = downstream_forks_by_filename
        self.default_downstream_stages = default_downstream_stages

    def __call__(self) -> Generator[str, str, None]:
        while True:
            image = yield
            stages = self.downstream_forks_by_filename.get(
                image.name, self.default_downstream_stages
            )
            if self.pipeline.verbosity >= 2:
                print(f"{self} sorting: {image}")
            if stages is not None:
                for stage in stages:
                    self.pipeline.stages[stage].send(image)

    # endregion
