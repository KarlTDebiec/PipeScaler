#!/usr/bin/env python
#   pipescaler/core/pipeline.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from copy import deepcopy
from importlib import import_module
from importlib.util import module_from_spec, spec_from_file_location
from os import makedirs
from os.path import basename, expandvars, isdir, isfile, join, splitext
from pprint import pprint
from shutil import copyfile
from typing import Any, Dict, List, TYPE_CHECKING

import numpy as np
from PIL import Image

from pipescaler.common import (
    DirectoryNotFoundError,
    get_name,
    validate_input_path,
    validate_int,
    validate_output_path,
)

if TYPE_CHECKING:
    from pipescaler.core import PipeImage, Stage


####################################### CLASSES ########################################
class StageRun:
    def __init__(self, stage):
        self.stage = stage
        self.inlets = {inlet: None for inlet in stage.inlets}
        self.outlets = {outlet: None for outlet in stage.outlets}

    def run(self):
        pass

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f"Run for {self.stage.name}\n  {self.inlets}\n  {self.outlets}"


class Pipeline:

    # region Builtins

    def __init__(
        self,
        pipeline: List[Any],
        stages: Dict[str, Dict[str, Any]],
        wip_directory: str,
        verbosity: int = 1,
    ) -> None:

        # Store configuration
        try:
            self.wip_directory = validate_output_path(
                wip_directory, file_ok=False, directory_ok=True
            )
        except DirectoryNotFoundError as e:
            makedirs(expandvars(wip_directory))
            self.wip_directory = validate_output_path(
                wip_directory, file_ok=False, directory_ok=True
            )
        self.verbosity = validate_int(verbosity, min_value=0)

        # Load configuration
        stage_modules = [
            import_module(f"pipescaler.{package}")
            for package in ["mergers", "processors", "sorters", "sources", "splitters"]
        ]

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
            self.stages[stage_name] = stage_cls(name=stage_name, **stage_args)

        # Configure pipeline
        # TODO: Validate
        self.pipeline = pipeline

    def __call__(self, **kwargs: Any) -> None:
        """Performs operations."""
        source = self.stages[self.pipeline[0]]

        for i, image in enumerate(source):
            print(f"{image} ({i})")
            directory = join(self.wip_directory, image.name)
            backup = join(directory, f"{image.name}.{image.ext}")
            if not isdir(directory):
                if self.verbosity >= 1:
                    print(f"    creating '{directory}'")
                makedirs(directory)
            if not isfile(backup):
                if self.verbosity >= 1:
                    print(f"    backing up to '{backup}'")
                copyfile(image.infile, backup)
            image.infile = backup
            self.process_image(image, self.pipeline[1:])

    def process_image(self, image, stages):
        # Prepare the stages
        stage_runs = []
        for stage_name in stages:
            if isinstance(stage_name, dict):
                outlet_stages = list(stage_name.values())[0]
                stage_name = list(stage_name.keys())[0]
            stage = self.stages[stage_name]
            stage_runs.append(StageRun(stage))
            print(stage, stage.inlets, stage.outlets)
        stage_runs[0].inlets[""] = image.infile
        pprint(stage_runs)

    # def process_image(self, image, infile, upstream, stages):
    #     stage_spec = stages.pop(0)
    #
    #     suffixes = []
    #     if isinstance(stage_spec, str):
    #         stage_name = stage_spec
    #     elif isinstance(stage_spec, dict):
    #         stage_name = list(stage_spec.keys())[0]
    #         downstream_2 = list(stage_spec.values())[0]
    #     else:
    #         raise ValueError()
    #     stage = self.stages[stage_name]
    #     print(f"  {stage}")
    #     if len(stage.inlets) == 1 and len(stage.outlets) == 1:
    #         suffixes.append(stage.suffix)
    #         outfile = join(self.wip_directory, image.name, f"{'_'.join(suffixes)}.png")
    #         if not isfile(outfile):
    #             inlet = Image.open(infile)
    #             outlet = stage.process(inlet)
    #             print(f"    Saving {outfile}")
    #             outlet.save(outfile)
    #         else:
    #             print(f"    Previously saved {outfile}")
    # elif len(stage.inlets) == 1 and len(stage.outlets) >= 2:
    #     outfiles = []
    #     for outlet in stage.outlets:
    #         suffixes_2 = deepcopy(suffixes)
    #         suffixes_2.append(outlet)
    #         outfiles.append(
    #             join(self.wip_directory, image.name, f"{'_'.join(suffixes_2)}.png",)
    #         )
    #     if not np.all([isfile(outfile) for outfile in outfiles]):
    #         inlet = Image.open(last_infile)
    #         outlets = stage.process(inlet)
    #         for outlet, outfile in zip(outlets, outfiles):
    #             print(f"    Saving {outfile}")
    #             outlet.save(outfile)
    #     else:
    #         for outfile in outfiles:
    #             print(f"    Previously saved {outfile}")
    #     print(downstream_2)
    # else:
    #     exit()

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
                print(f"    creating '{directory}'")
            makedirs(directory)
        if not isfile(backup):
            if self.verbosity >= 1:
                print(f"    backing up to '{backup}'")
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
