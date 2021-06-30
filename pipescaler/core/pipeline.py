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
        print()
        pprint(self.pipeline)

        # Initialize directory
        if not isdir(self.wip_directory):
            if self.verbosity >= 1:
                print(f"Creating directory '{self.wip_directory}'")
            makedirs(self.wip_directory)

    def build_source(self, stage_cls, downstream_pipeline_conf):
        downstream_pipeline = [stage_cls]
        downstream_pipeline.extend(self.build_route(downstream_pipeline_conf))

        return downstream_pipeline

    def build_merger(self, stage_cls, inlet, downstream_pipeline_conf):
        if inlet is not None:
            downstream_pipeline = [{stage_cls: inlet}]
        else:
            downstream_pipeline = [stage_cls]

        downstream_pipeline.extend(self.build_route(downstream_pipeline_conf))

        return downstream_pipeline

    def build_processor(self, stage_cls, downstream_pipeline_conf):
        downstream_pipeline = [stage_cls]
        downstream_pipeline.extend(self.build_route(downstream_pipeline_conf))

        return downstream_pipeline

    def build_sorter(self, stage_cls, stage_conf):
        downstream_pipeline = [{stage_cls: {}}]

        for outlet in filter(lambda o: o in stage_conf, stage_cls.outlets):
            downstream_pipeline[0][stage_cls][outlet] = self.build_route(
                stage_conf.pop(outlet)
            )

        return downstream_pipeline

    def build_splitter(self, stage_cls, stage_conf, downstream_pipeline_conf):
        downstream_pipeline = [{stage_cls: {}}]

        for outlet in filter(lambda o: o in stage_conf, stage_cls.outlets):
            downstream_pipeline[0][stage_cls][outlet] = self.build_route(
                stage_conf.pop(outlet)
            )

        downstream_pipeline.extend(self.build_route(downstream_pipeline_conf))

        return downstream_pipeline

    def build_route(self, downstream_pipeline_conf):
        if not isinstance(downstream_pipeline_conf, List):
            raise ValueError()
        if len(downstream_pipeline_conf) == 0:
            return []

        if isinstance(downstream_pipeline_conf[0], str):
            stage_name = downstream_pipeline_conf.pop(0)
            stage_conf = None
        elif isinstance(downstream_pipeline_conf[0], dict):
            stage_name, stage_conf = next(iter(downstream_pipeline_conf.pop(0).items()))
        else:
            raise ValueError()
        stage = self.stages[stage_name]

        if isinstance(stage, Merger):
            return self.build_merger(stage, stage_conf, downstream_pipeline_conf)
        elif isinstance(stage, Processor):
            return self.build_processor(stage, downstream_pipeline_conf)
        elif isinstance(stage, Sorter):
            return self.build_sorter(stage, stage_conf)
        elif isinstance(stage, Splitter):
            return self.build_splitter(stage, stage_conf, downstream_pipeline_conf)

    def __call__(self, **kwargs: Any) -> None:
        """Performs operations."""
        pass
        # source = self.pipeline[0]

    #         for outlets in source:
    #             infile = outlets["outlet"]
    #             image = PipeImage(infile)
    #             infile = self.backup(image)
    #             print(infile)
    #             for stage in self.pipeline[1:]:
    #                 if len(stage.outlets) != 0:
    #                     outfile = self.get_outfile(image, infile, stage)
    #                     print(infile, outfile)
    #                     stage(infile, outfile)
    #                     infile = outfile

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
