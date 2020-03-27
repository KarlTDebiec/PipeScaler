#!python
#   lauseuisin/Pipeline.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
################################### MODULES ###################################
from __future__ import annotations

from importlib import import_module
from os import W_OK, access, getcwd, listdir
from os.path import expandvars, isdir
from pathlib import Path
from subprocess import Popen
from typing import Any, Dict, List
from os import remove

from IPython import embed


################################### CLASSES ###################################
class Pipeline:
    # region Class Variables

    package_root: str = str(Path(__file__).parent.absolute())

    # endregion

    # region Builtins

    def __init__(self, conf: Dict[Any, Any], verbosity: int = 1) -> None:

        # Store global configuration
        self.verbosity = verbosity
        self.wip_directory = expandvars(conf.get("wip_directory", getcwd()))
        if not isdir(self.wip_directory) and access(self.wip_directory, W_OK):
            raise ValueError()

        # Load configuration
        sources_module = import_module("lauhseuisin.sources")
        processors_module = import_module("lauhseuisin.processors")
        sorters_module = import_module("lauhseuisin.sorters")
        pipes_conf = conf.get("pipes")
        if pipes_conf is None:
            raise ValueError()

        # Configure source
        source_conf = pipes_conf.pop("source")
        if source_conf is None:
            raise ValueError()
        source_cls_name = list(source_conf.keys())[0]
        source_cls_parameters = list(source_conf.values())[0]
        source_cls = getattr(sources_module, source_cls_name)
        self.source = source_cls(pipeline=self, **source_cls_parameters)

        # Configure sorters and processors
        pipes = {}
        for pipe_name, pipe_conf in pipes_conf.items():
            pipe_cls_name = list(pipe_conf.keys())[0]
            pipe_cls_parameters = list(pipe_conf.values())[0]
            if pipe_cls_parameters is None:
                pipe_cls_parameters = {}
            print(pipe_cls_name)
            print(pipe_cls_parameters)
            try:
                pipe_cls = getattr(processors_module, pipe_cls_name)
            except AttributeError:
                pipe_cls = getattr(sorters_module, pipe_cls_name)
            pipes[pipe_name] = pipe_cls(pipeline=self, **pipe_cls_parameters)()
            next(pipes[pipe_name])
        self.pipes = pipes

        # Prepare log
        self.log: Dict[str, List[str]] = {}

    def __call__(self) -> None:
        """
        Performs operations
        """
        self.source()
        self.clean()

    def clean(self):
        for name, outfiles in self.log.items():
            for f in listdir(f"{self.wip_directory}/{name}"):
                if f == "original.png":
                    continue
                if f not in outfiles:
                    print(f"Removing '{self.wip_directory}/{name}/{f}'")
                    remove(f"{self.wip_directory}/{name}/{f}")

    # endregion
