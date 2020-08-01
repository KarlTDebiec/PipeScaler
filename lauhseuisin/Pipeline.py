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

import importlib
from os import W_OK, access, getcwd, listdir, remove
from os.path import basename, expandvars, isdir, splitext
from pathlib import Path
from shutil import rmtree
from typing import Any, Dict, List


################################### CLASSES ###################################
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
        sources_module = importlib.import_module("lauhseuisin.sources")
        processors_module = importlib.import_module("lauhseuisin.processors")
        sorters_module = importlib.import_module("lauhseuisin.sorters")
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
                spec = importlib.util.spec_from_file_location(
                    splitext(basename(module_path))[0], module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                pipe_cls = getattr(module, pipe_cls_name)
            else:
                try:
                    pipe_cls = getattr(processors_module, pipe_cls_name)
                except AttributeError:
                    try:
                        pipe_cls = getattr(sorters_module, pipe_cls_name)
                    except AttributeError as e:
                        raise e
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
