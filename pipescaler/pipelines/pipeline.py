#!/usr/bin/env python
#   pipescaler/pipeline.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from importlib import import_module
from importlib.util import module_from_spec, spec_from_file_location
from os import W_OK, access, getcwd, listdir, remove
from os.path import basename, expandvars, isdir, splitext
from pathlib import Path
from shutil import rmtree
from typing import Any, Dict, List


####################################### CLASSES ########################################
class Pipeline:
    package_root: str = str(Path(__file__).parent.absolute())

    # region Builtins

    def __init__(self, conf: Dict[Any, Any], verbosity: int = 1) -> None:

        # Store global configuration
        self.verbosity = verbosity
        self.wip_directory = expandvars(conf.get("wip_directory", getcwd()))
        if not isdir(self.wip_directory) and access(self.wip_directory, W_OK):
            raise ValueError()

        # Load configuration
        sources_module = import_module("pipescaler.sources")
        mergers_module = import_module("pipescaler.mergers")
        processors_module = import_module("pipescaler.processors")
        sorters_module = import_module("pipescaler.sorters")
        splitters_module = import_module("pipescaler.splitters")
        modules = [mergers_module, processors_module, sorters_module, splitters_module]
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
            if "module" in pipe_conf:
                module_path = expandvars(pipe_conf.pop("module"))
            else:
                module_path = None
            pipe_cls_name = list(pipe_conf.keys())[0]
            pipe_cls_parameters = list(pipe_conf.values())[0]
            if pipe_cls_parameters is None:
                pipe_cls_parameters = {}
            print(pipe_cls_name)
            print(pipe_cls_parameters)
            if module_path is not None:
                spec = spec_from_file_location(
                    splitext(basename(module_path))[0], module_path
                )
                module = module_from_spec(spec)
                spec.loader.exec_module(module)
                pipe_cls = getattr(module, pipe_cls_name)
            else:
                pipe_cls = None
                for module in modules:
                    try:
                        pipe_cls = getattr(module, pipe_cls_name)
                    except AttributeError:
                        continue
                if pipe_cls is None:
                    raise AttributeError(f"Class {pipe_cls_name} not found")
            pipes[pipe_name] = pipe_cls(pipeline=self, **pipe_cls_parameters)()
            next(pipes[pipe_name])
        self.pipes = pipes

        # Prepare log
        self.log: Dict[str, List[str]] = {}

    def __call__(self) -> None:
        """Performs operations."""
        self.source()
        # self.clean()

    def clean(self) -> None:
        for name, outfiles in self.log.items():
            for f in listdir(f"{self.wip_directory}/{name}"):
                if f == "original.png":
                    continue
                if f not in outfiles:
                    print(f"Removing '{self.wip_directory}/{name}/{f}'")
                    remove(f"{self.wip_directory}/{name}/{f}")
        for name in listdir(f"{self.wip_directory}"):
            if name not in self.log and isdir(f"{self.wip_directory}/{name}"):
                print(f"Removing '{self.wip_directory}/{name}'")
                rmtree(f"{self.wip_directory}/{name}")

    # endregion
