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
from pprint import pprint
from shutil import copyfile
from typing import Any, Dict, List, TYPE_CHECKING, Union

from pipescaler.common import (
    get_name,
    validate_int,
    validate_output_path,
)
from pipescaler.core import (
    Merger,
    PipeImage,
    Processor,
    Sorter,
    Splitter,
)

if TYPE_CHECKING:
    from pipescaler.core import Stage


####################################### CLASSES ########################################
class Pipeline:

    # region Builtins

    def __init__(
        self,
        wip_directory: str,
        stages: Dict[str, Dict[str, Dict[str, Any]]],
        pipeline: List[Union[str, Dict[str, Any]]],
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
            # Get stage's class name
            stage_cls_name = next(iter(stage_conf))  # get first key

            # Get stage's class
            stage_cls = None
            for module in stage_modules:
                try:
                    stage_cls = getattr(module, stage_cls_name)
                except AttributeError:
                    continue
            if stage_cls is None:
                raise AttributeError(f"Class '{stage_cls_name}' not found")

            # Get stage's arguments
            stage_args = stage_conf.get(stage_cls_name)
            if stage_args is None:
                stage_args = {}

            # Initialize stage
            self.stages[stage_name] = stage_cls(name=stage_name, **stage_args)

        # Initialize pipeline
        stage_name = pipeline.pop(0)
        if stage_name in self.stages:
            stage = self.stages[stage_name]
        else:
            raise KeyError()
        self.pipeline = self.build_source(stage, pipeline)
        if self.verbosity >= 1:
            pprint(self.pipeline)

        # Initialize directory
        if not isdir(self.wip_directory):
            if self.verbosity >= 1:
                print(f"Creating directory '{self.wip_directory}'")
            makedirs(self.wip_directory)

    def __call__(self, **kwargs: Any) -> None:
        """Performs operations."""
        source = self.pipeline[0]

        for infile in source:
            image = PipeImage(infile)

            # Create image working directory
            image_directory = validate_output_path(
                join(self.wip_directory, image.name), file_ok=False, directory_ok=True
            )
            if not isdir(image_directory):
                if self.verbosity >= 1:
                    print(f"Creating directory '{image_directory}'")
                makedirs(image_directory)

            # Backup original image to working directory
            image_backup = join(image_directory, image.filename)
            if not isfile(image_backup):
                if self.verbosity >= 1:
                    print(f"Copying '{image.full_path}' to '{outfile}'")
                copyfile(image.full_path, outfile)

            # Flow into pipeline
            stage = self.pipeline[1]
            if isinstance(stage, Processor):
                outfile = join(
                    self.wip_directory, image.name, image.get_outfile(stage, infile)
                )
                if not isfile(outfile):
                    stage(infile=infile, outfile=outfile, verbosity=self.verbosity)

    def run_processor(self, stage, downstream_pipeline):
        pass

    def __repr__(self) -> str:
        return self.__class__.__name__.lower()

    def __str__(self) -> str:
        return self.__class__.__name__.lower()

    # endregion

    # region Methods

    def build_source(self, stage, pipeline_conf):
        pipeline = [stage]
        pipeline.extend(self.build_route(pipeline_conf))

        return pipeline

    def build_merger(self, stage, inlet, pipeline_conf):
        if inlet is not None:
            pipeline = [{stage: inlet}]
        else:
            pipeline = [stage]

        pipeline.extend(self.build_route(pipeline_conf))

        return pipeline

    def build_processor(self, stage, pipeline_conf):
        pipeline = [stage]
        pipeline.extend(self.build_route(pipeline_conf))

        return pipeline

    def build_sorter(self, stage, stage_conf):
        pipeline = [{stage: {}}]

        for outlet in filter(lambda o: o in stage_conf, stage.outlets):
            pipeline[0][stage][outlet] = self.build_route(stage_conf.pop(outlet))

        return pipeline

    def build_splitter(self, stage, stage_conf, pipeline_conf):
        pipeline = [{stage: {}}]

        for outlet in filter(lambda o: o in stage_conf, stage.outlets):
            pipeline[0][stage][outlet] = self.build_route(stage_conf.pop(outlet))
        pipeline.extend(self.build_route(pipeline_conf))

        return pipeline

    def build_route(self, pipeline_conf):
        if not isinstance(pipeline_conf, List):
            raise ValueError()
        if len(pipeline_conf) == 0:
            return []

        if isinstance(pipeline_conf[0], str):
            stage_name = pipeline_conf.pop(0)
            stage_conf = None
        elif isinstance(pipeline_conf[0], dict):
            stage_name, stage_conf = next(iter(pipeline_conf.pop(0).items()))
        else:
            raise ValueError()
        stage = self.stages[stage_name]

        if isinstance(stage, Merger):
            return self.build_merger(stage, stage_conf, pipeline_conf)
        elif isinstance(stage, Processor):
            return self.build_processor(stage, pipeline_conf)
        elif isinstance(stage, Sorter):
            return self.build_sorter(stage, stage_conf)
        elif isinstance(stage, Splitter):
            return self.build_splitter(stage, stage_conf, pipeline_conf)

    # endregion
