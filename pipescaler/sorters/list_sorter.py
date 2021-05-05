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

from os import listdir
from os.path import isdir
from typing import Any, Dict, Generator

import yaml

from pipescaler.common import get_name, validate_input_path
from pipescaler.core import Sorter


####################################### CLASSES ########################################
class ListSorter(Sorter):
    """
    TODO: map filename to fork at runtime rather than creating a list beforehand
    """

    # region Builtins

    def __init__(self, forks: Dict[str, Dict[str, Any]], **kwargs: Any) -> None:
        super().__init__(**kwargs)

        # Store configuration
        desc = f"{self.name} {self.__class__.__name__}"

        # Organize downstream forks
        forks_by_filename = {}
        default_fork_name = None
        default_downstream_stages = None
        for fork_name, fork_conf in forks.items():
            if fork_conf is None:
                fork_conf = {}

            # Parse filenames for this fork
            input_filenames = fork_conf.get("filenames")

            if input_filenames is None:
                if default_fork_name is not None:
                    raise ValueError(
                        "At most one configuration may omit 'filenames' and will be "
                        "used as the default fork; two or more have been provided."
                    )
                default_fork_name = fork_name
                downstream_stages = fork_conf.get("downstream_stages")
                if isinstance(downstream_stages, str):
                    downstream_stages = [downstream_stages]
                default_downstream_stages = downstream_stages
                continue

            if isinstance(input_filenames, str):
                input_filenames = [input_filenames]
            filenames = set()
            for input_filename in input_filenames:
                try:
                    input_filename = validate_input_path(
                        input_filename, file_ok=True, directory_ok=True
                    )
                    if isdir(input_filename):
                        filenames |= {get_name(f) for f in listdir(input_filename)}
                    else:
                        with open(input_filename, "r") as f:
                            filenames |= {
                                get_name(f)
                                for f in yaml.load(f, Loader=yaml.SafeLoader)
                            }
                except FileNotFoundError:
                    filenames |= {get_name(input_filename)}
                filenames.discard(".DS_Store")
            desc += f"\n ├─ {fork_name} ({len(filenames)} filenames)"

            # Parse downstream stages for this class
            downstream_stages = fork_conf.get("downstream_stages")
            if isinstance(downstream_stages, str):
                downstream_stages = [downstream_stages]
            for filename in filenames:
                forks_by_filename[filename] = downstream_stages
            if downstream_stages is not None:
                if len(downstream_stages) >= 2:
                    for stage in downstream_stages:
                        desc += f"\n │   ├─ {stage}"
                desc += f"\n │   └─ {downstream_stages[-1]}"
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
        self.forks_by_filename = forks_by_filename
        self.default_downstream_stages = default_downstream_stages
        print(self.forks_by_filename)

    def __call__(self) -> Generator[str, str, None]:
        while True:
            image = yield
            stages = self.forks_by_filename.get(
                image.name, self.default_downstream_stages
            )
            if self.pipeline.verbosity >= 2:
                print(f"  {self}")
            if stages is not None:
                for stage in stages:
                    self.pipeline.stages[stage].send(image)

    # endregion
