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

import logging
from importlib import import_module
from logging import info, warning
from os import makedirs
from os.path import isdir, isfile, join
from pprint import pformat
from shutil import copyfile
from typing import Any, Dict, List, Union

from pipescaler.common import (
    validate_int,
    validate_output_path,
)
from pipescaler.core import (
    Merger,
    PipeImage,
    Processor,
    Sorter,
    Splitter,
    Stage,
    UnsupportedPlatformError,
)


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
        if self.verbosity == 1:
            logging.basicConfig(level=logging.WARNING)
        elif self.verbosity == 2:
            logging.basicConfig(level=logging.INFO)
        elif self.verbosity == 3:
            logging.basicConfig(level=logging.DEBUG)

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

            # Get stage's configuration
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
        info(f"{self}: {pformat(self.pipeline)}")

        # Initialize directory
        if not isdir(self.wip_directory):
            info(f"{self}: '{self.wip_directory}' created")
            makedirs(self.wip_directory)

    def __call__(self, **kwargs: Any) -> None:
        """Performs operations."""
        source = self.pipeline[0]

        for infile in source:
            info(f"{self}: '{infile}' processing started")
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
            # TODO: Should be handled within source, to support archive sources
            image_backup = join(image_directory, image.filename)
            if not isfile(image_backup):
                copyfile(image.full_path, image_backup)
                info(f"{self}: '{image.full_path}' copied to '{image_backup}'")

            # Flow into pipeline
            try:
                self.run_route(
                    pipeline=self.pipeline[1:], image=image, infile=image_backup
                )
            except UnsupportedPlatformError as e:
                warning(
                    f"{self}: While processing '{image.name}', encountered "
                    f"UnsupportedPlatformError '{e}', continuing on to next image"
                )

    def __repr__(self) -> str:
        return self.__class__.__name__.lower()

    def __str__(self) -> str:
        return self.__class__.__name__.lower()

    # endregion

    # region Methods

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

    def build_route(self, pipeline_conf):
        if pipeline_conf is None:
            return []
        elif not isinstance(pipeline_conf, List):
            raise ValueError()
        elif len(pipeline_conf) == 0:
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
            return self.build_sorter(stage, stage_conf, pipeline_conf)
        elif isinstance(stage, Splitter):
            return self.build_splitter(stage, stage_conf, pipeline_conf)
        else:
            raise ValueError()

    def build_sorter(self, stage, stage_conf, pipeline_conf):
        pipeline = [{stage: {}}]

        for outlet in filter(lambda o: o in stage_conf, stage.outlets):
            pipeline[0][stage][outlet] = self.build_route(stage_conf.pop(outlet))
        pipeline.extend(self.build_route(pipeline_conf))

        return pipeline

    def build_source(self, stage, pipeline_conf):
        pipeline = [stage]
        pipeline.extend(self.build_route(pipeline_conf))

        return pipeline

    def build_splitter(self, stage, stage_conf, pipeline_conf):
        pipeline = [{stage: {}}]

        if stage_conf is not None:
            for outlet in filter(lambda o: o in stage_conf, stage.outlets):
                pipeline[0][stage][outlet] = self.build_route(stage_conf.pop(outlet))
        pipeline.extend(self.build_route(pipeline_conf))

        return pipeline

    def run_merger(self, stage, stage_pipeline, image, **kwargs):
        if isinstance(stage_pipeline, str):
            return {stage_pipeline: kwargs["infile"]}

        outfile = join(
            self.wip_directory,
            image.name,
            image.get_outfile(
                kwargs[stage.inlets[0]],
                stage.suffix,
                stage.trim_suffixes,
                stage.extension,
            ),
        )
        if not isfile(outfile):
            stage(outfile=outfile, **kwargs)
        else:
            info(f"{self}: '{outfile}' already exists")

        return self.run_route(image=image, infile=outfile, **kwargs)

    def run_processor(self, stage, image, infile, **kwargs):
        outfile = join(
            self.wip_directory,
            image.name,
            image.get_outfile(
                infile, stage.suffix, stage.trim_suffixes, stage.extension
            ),
        )
        if not isfile(outfile):
            stage(infile=infile, outfile=outfile)
        else:
            info(f"{self}: '{outfile}' already exists")

        return self.run_route(image=image, infile=outfile, **kwargs)

    def run_sorter(self, stage, stage_pipeline, infile, pipeline, **kwargs):
        outlet_name = stage(infile=infile)

        outfile = self.run_route(
            infile=infile, pipeline=stage_pipeline.get(outlet_name, []), **kwargs
        )

        return self.run_route(infile=outfile, pipeline=pipeline, **kwargs)

    def run_splitter(self, stage, stage_pipeline, image, infile, **kwargs):
        outfiles = {
            outlet: join(
                self.wip_directory,
                image.name,
                image.get_outfile(
                    infile,
                    stage.suffixes[outlet],
                    stage.trim_suffixes,
                    stage.extension,
                ),
            )
            for outlet in stage.outlets
        }
        to_run = False
        for outfile in outfiles.values():
            if not isfile(outfile):
                to_run = True
            else:
                info(f"{self}: '{outfile}' already exists")
        if to_run:
            stage(infile=infile, verbosity=self.verbosity, **outfiles)

        downstream_inlets = {}
        for outlet_name in stage.outlets:
            outfile = outfiles[outlet_name]
            outlet_pipeline = stage_pipeline.get(outlet_name, [])
            nay = self.run_route(pipeline=outlet_pipeline, image=image, infile=outfile)

            if isinstance(nay, dict):
                downstream_inlets.update(nay)
            else:
                raise ValueError()
        kwargs.update(downstream_inlets)

        return self.run_route(image=image, **kwargs)

    def run_route(self, pipeline, **kwargs):
        if pipeline is None:
            return kwargs.get("infile", None)
        elif not isinstance(pipeline, List):
            raise ValueError()
        elif len(pipeline) == 0:
            return kwargs.get("infile", None)

        if isinstance(pipeline[0], Stage):
            kwargs["stage"], kwargs["stage_pipeline"] = pipeline[0], None
        elif isinstance(pipeline[0], dict):
            kwargs["stage"], kwargs["stage_pipeline"] = next(iter(pipeline[0].items()))
        else:
            raise ValueError()

        kwargs["pipeline"] = pipeline[1:]

        if isinstance(kwargs["stage"], Merger):
            return self.run_merger(**kwargs)
        elif isinstance(kwargs["stage"], Processor):
            return self.run_processor(**kwargs)
        elif isinstance(kwargs["stage"], Sorter):
            return self.run_sorter(**kwargs)
        elif isinstance(kwargs["stage"], Splitter):
            return self.run_splitter(**kwargs)
        else:
            raise ValueError()

    # endregion
