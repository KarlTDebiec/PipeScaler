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
from os import makedirs
from os.path import basename, isdir, isfile, join, splitext
from shutil import copyfile
from typing import Any, Dict, TYPE_CHECKING

from pipescaler.common import (
    get_name,
    validate_input_path,
    validate_int,
    validate_output_path,
)

if TYPE_CHECKING:
    from pipescaler.core import PipeImage, Stage


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

        # Store configuration
        self.wip_directory = validate_output_path(
            wip_directory, file_ok=False, directory_ok=True
        )
        self.verbosity = validate_int(verbosity, min_value=0)

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
        self.stages: Dict[str, Stage] = {}
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
            print(repr(stage))
            self.stages[stage_name] = stage()
            next(self.stages[stage_name])

    def __call__(self, **kwargs: Any) -> None:
        """Performs operations."""
        source = self.source()
        next(source)
        for image in self.source:
            source.send(image)

    def __repr__(self) -> str:
        return self.__class__.__name__.lower()

    def __str__(self) -> str:
        return self.__class__.__name__.lower()

    # endregion

    # region Methods

    def backup(self, image: PipeImage) -> None:
        directory = join(self.wip_directory, image.name)
        backup = join(directory, f"{image.name}.{image.ext}")
        if not isdir(directory):
            if self.verbosity >= 1:
                print(f"{self} creating: {dir()}")
            makedirs(directory)
        if not isfile(backup):
            if self.verbosity >= 1:
                print(f"{self} backing up to: {backup}")
            copyfile(image.infile, backup)

    def get_outfile(self, image, suffix, lstrip="_", rstrip=None):
        self.backup(image)
        if len(image.history) >= 1:
            filename = f"{get_name(image.last)}"
            if lstrip is not None:
                filename = filename.lstrip(lstrip)
            if rstrip is not None:
                filename = filename.rstrip(rstrip)
            filename = f"{filename}_{suffix}".lstrip("_")
        else:
            filename = suffix
        return join(self.wip_directory, image.name, f"{filename}.png")

    # endregion
