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

from importlib import import_module
from os import makedirs
from os.path import basename, isdir, isfile, join
from shutil import copyfile
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from pipescaler.common import (
    get_name,
    validate_int,
    validate_output_path,
)
from pipescaler.core import Block, PipeImage, Source

if TYPE_CHECKING:
    from pipescaler.core import Stage


####################################### CLASSES ########################################
class Pipeline:

    # region Builtins

    def __init__(
        self,
        wip_directory: str,
        stages: Dict[str, Dict[str, Dict[str, Any]]],
        pipeline: Dict[str, Dict[str, Any]],
        blocks: Optional[Dict[str, Dict[str, Any]]] = None,
        verbosity: int = 1,
    ) -> None:

        # Store configuration
        self.wip_directory = validate_output_path(
            wip_directory, file_ok=False, directory_ok=True
        )
        self.verbosity = validate_int(verbosity, min_value=0)

        # Load configuration
        stage_modules = [
            import_module(f"pipescaler.{package}")
            for package in ["mergers", "processors", "sorters", "sources", "splitters"]
        ]

        # Initialize stages
        self.stages: Dict[str, Stage] = {}
        for stage_name, stage_conf in stages.items():
            stage_cls_name = next(iter(stage_conf))
            stage_args = stage_conf.get(stage_cls_name, {})
            stage_cls = None
            for module in stage_modules:
                try:
                    stage_cls = getattr(module, stage_cls_name)
                except AttributeError:
                    continue
            if stage_cls is None:
                raise AttributeError(f"Class {stage_cls_name} not found")
            self.stages[stage_name] = stage_cls(name=stage_name, **stage_args)

        # Initialize blocks
        self.blocks = {}
        for block_name, block_conf in blocks.items():
            if block_name in self.stages:
                raise KeyError()
            block_stages = []
            for stage_name in block_conf:
                if stage_name not in self.stages:
                    raise KeyError()
            preceding_stage_outlets = self.stages[block_conf[0]].inlets
            for stage_name in block_conf:
                stage = self.stages[stage_name]
                if stage.inlets != preceding_stage_outlets:
                    raise ValueError()
            self.blocks[block_name] = Block(block_stages, name=block_name)

        # Initialize pipeline
        self.pipeline: List[Stage] = []
        for stage_name in pipeline:
            if stage_name in self.stages:
                self.pipeline.append(self.stages[stage_name])
            elif stage_name in self.blocks:
                self.pipeline.append(self.blocks[stage_name])
            else:
                raise KeyError()
        if not isinstance(self.pipeline[0], Source):
            raise ValueError()

        # Initialize directory
        if not isdir(self.wip_directory):
            if self.verbosity >= 1:
                print(f"Creating directory '{self.wip_directory}'")
            makedirs(self.wip_directory)

    def __call__(self, **kwargs: Any) -> None:
        """Performs operations."""
        for infile in self.pipeline[0]:
            image = PipeImage(infile)
            infile = self.backup(image)
            print(infile)
            for stage in self.pipeline[1:]:
                if len(stage.outlets) != 0:
                    outfile = self.get_outfile(image, infile, stage)
                    print(infile, outfile)
                    stage(infile, outfile)
                    infile = outfile

    def __repr__(self) -> str:
        return self.__class__.__name__.lower()

    def __str__(self) -> str:
        return self.__class__.__name__.lower()

    # endregion

    # region Methods

    def backup(self, image: PipeImage) -> str:
        output_directory = validate_output_path(
            join(self.wip_directory, image.name), file_ok=False, directory_ok=True
        )
        if not isdir(output_directory):
            if self.verbosity >= 1:
                print(f"Creating directory '{output_directory}'")
            makedirs(output_directory)

        outfile = join(output_directory, basename(image.full_path))
        if not isfile(outfile):
            if self.verbosity >= 1:
                print(f"Copying '{image.full_path}' to '{outfile}'")
            copyfile(image.full_path, outfile)

        return outfile

    def get_outfile(self, image: PipeImage, infile: str, stage: Stage):
        prefix = get_name(infile)
        if prefix.startswith(image.name):
            prefix = prefix[len(image.name) :]
        outfile = f"{prefix}_{stage.suffix}.png"
        outfile = outfile.lstrip("_")

        return join(self.wip_directory, image.name, outfile)

    # endregion
