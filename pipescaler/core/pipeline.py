#!/usr/bin/env python
#   pipescaler/core/pipeline.py
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
from os import listdir, remove
from os.path import basename, isdir, splitext
from shutil import rmtree
from typing import Any, Dict, TYPE_CHECKING

from pipescaler.common import validate_input_path, validate_int, validate_output_path

if TYPE_CHECKING:
    from pipescaler.core.source import Source
    from pipescaler.core.stage import Stage


####################################### CLASSES ########################################
class Pipeline:

    # region Builtins

    def __init__(
        self,
        wip_directory: str,
        source: Dict[str, Dict[str, Any]],
        stages: Dict[str, Dict[str, Any]],
        verbosity: int = 1,
    ) -> None:

        # Store global configuration
        self.verbosity = verbosity
        self.wip_directory = wip_directory

        # Load configuration
        sources_module = import_module("pipescaler.sources")
        stage_modules = [
            import_module(f"pipescaler.{package}")
            for package in ["mergers", "processors", "sorters", "splitters"]
        ]

        # Configure source
        source_cls_name = list(source.keys())[0]
        source_args = list(source.values())[0]
        source_cls = getattr(sources_module, source_cls_name)
        self.source = source_cls(pipeline=self, **source_args)
        print(repr(self.source))

        # Configure stages
        self.stages = {}
        for stage_name, stage_conf in stages.items():
            if "module" in stage_conf:
                module_path = validate_input_path(stage_conf.pop("module"))
            else:
                module_path = None
            stage_cls_name = list(stage_conf.keys())[0]
            stage_args = list(stage_conf.values())[0]
            if stage_args is None:
                stage_args = {}
            if module_path is not None:
                spec = spec_from_file_location(
                    splitext(basename(module_path))[0], module_path
                )
                module = module_from_spec(spec)
                spec.loader.exec_module(module)
                stage_cls = getattr(module, stage_cls_name)
            else:
                stage_cls = None
                for module in stage_modules:
                    try:
                        stage_cls = getattr(module, stage_cls_name)
                    except AttributeError:
                        continue
                if stage_cls is None:
                    raise AttributeError(f"Class {stage_cls_name} not found")
            stage = stage_cls(pipeline=self, name=stage_name, **stage_args)
            stages[stage_name] = stage()
            next(stages[stage_name])
            print(repr(stage))
        self.stages = stages

    def __call__(self, **kwargs: Any) -> None:
        """Performs operations."""
        source = self.source()
        next(source)
        for image in self.source:
            source.send(image)
        # self.clean()

    def __repr__(self) -> str:
        return self.__class__.__name__

    def __str__(self) -> str:
        return self.__class__.__name__

    # endregion

    # region Properties

    @property
    def source(self) -> Source:
        """Source: Source"""
        return self._source

    @source.setter
    def source(self, value: Source) -> None:
        self._source = value

    @property
    def stages(self) -> Dict[str, Stage]:
        """Dict[str, Stage]: Stages."""
        return self._stages

    @stages.setter
    def stages(self, value: Dict[str, Stage]) -> None:
        self._stages = value

    @property
    def verbosity(self) -> int:
        """int: Level of output to provide"""
        if not hasattr(self, "_verbosity"):
            self._verbosity = 1
        return self._verbosity

    @verbosity.setter
    def verbosity(self, value: int) -> None:
        self._verbosity = validate_int(value, min_value=0)

    @property
    def wip_directory(self) -> str:
        """str: Path to work-in-progress directory"""
        return self._wip_directory

    @wip_directory.setter
    def wip_directory(self, value: str) -> None:
        self._wip_directory = validate_output_path(
            value, file_ok=False, directory_ok=True
        )

    # endregion

    # region Methods

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
