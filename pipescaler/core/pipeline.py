#!/usr/bin/env python
#   pipescaler/core/pipeline.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
""""""
from __future__ import annotations

from glob import glob
from importlib import import_module
from logging import info, warning
from os import listdir, makedirs, remove, rmdir
from os.path import basename, isdir, isfile, join, splitext
from pprint import pformat
from shutil import copyfile
from typing import Any, Dict, List, Optional, Union

from pipescaler.common import validate_output_path
from pipescaler.core import (
    Merger,
    PipeImage,
    Processor,
    Sorter,
    Source,
    Splitter,
    Stage,
    Terminus,
    TerminusReached,
    UnsupportedPlatformError,
)


class Pipeline:
    def __init__(
        self,
        wip_directory: str,
        stages: Dict[str, Dict[str, Dict[str, Any]]],
        pipeline: List[Union[str, Dict[str, Any]]],
        purge_wip: bool = False,
    ) -> None:

        # Store configuration
        self.wip_directory = validate_output_path(
            wip_directory, file_ok=False, directory_ok=True, create_directory=True
        )
        self.purge_wip = purge_wip

        # Load configuration
        stage_modules = [
            import_module(f"pipescaler.{package}")
            for package in [
                "mergers",
                "processors",
                "sorters",
                "sources",
                "splitters",
                "termini",
            ]
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
                raise KeyError(f"Class '{stage_cls_name}' not found")

            # Get stage's configuration
            stage_args = stage_conf.get(stage_cls_name)
            if stage_args is None:
                stage_args = {}

            # Initialize stage
            self.stages[stage_name] = stage_cls(name=stage_name, **stage_args)

        # Initialize pipeline
        if len(pipeline) == 0:
            raise ValueError("Pipeline must contain at least one stage")
        stage_name = pipeline.pop(0)
        if stage_name in self.stages:
            stage = self.stages[stage_name]
        else:
            raise KeyError(f"Stage {stage_name} referenced by pipeline does not exist")
        self.pipeline = self.build_source(stage, pipeline)
        info(f"{self}: {pformat(self.pipeline)}")

        # Initialize directory
        if not isdir(self.wip_directory):
            info(f"{self}: '{self.wip_directory}' created")
            makedirs(self.wip_directory)
        self.wip_files = set()

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
                info(f"{self}: '{image_directory}' created")
                makedirs(image_directory)

            # Backup original image to working directory
            # TODO: Should be handled within source, to support archive sources
            image_backup = join(image_directory, image.orig_filename)
            if not isfile(image_backup):
                copyfile(image.orig_full_path, image_backup)
                info(f"{self}: '{image.orig_full_path}' copied to '{image_backup}'")
            self.log_wip_file(image_backup)

            # Flow into pipeline
            try:
                self.run_route(
                    downstream_pipeline=self.pipeline[1:],
                    image=image,
                    infile=image_backup,
                )
            except TerminusReached:
                continue
            except UnsupportedPlatformError as error:
                warning(
                    f"{self}: While processing '{image.name}', encountered "
                    f"UnsupportedPlatformError '{error}', continuing on to next image"
                )

        if self.purge_wip:
            for wip_file in glob(f"{self.wip_directory}/**/*"):
                if wip_file not in self.wip_files:
                    remove(wip_file)
                    info(f"{self}: '{wip_file}' removed")
            for wip_subdirectory in glob(f"{self.wip_directory}/*"):
                if len(listdir(wip_subdirectory)) == 0:
                    rmdir(wip_subdirectory)
                    info(f"{self}: '{wip_subdirectory}' removed")

    def __repr__(self) -> str:
        return self.__class__.__name__.lower()

    def __str__(self) -> str:
        return self.__class__.__name__.lower()

    def build_merger(
        self,
        stage: Merger,
        stage_conf: Optional[str],
        downstream_pipeline_conf: List[Union[str, Dict[str, Any]]],
    ) -> List[Union[Stage, Dict[Stage, Any]]]:
        """
        Builds a merger and its downstream pipeline.

        Args:
            stage: Stage being built
            stage_conf: Configuration of this stage
            downstream_pipeline_conf: Configuration of downstream pipeline

        Returns:
             Pipeline including this stage and those downstream
        """
        if stage_conf is None:
            pipeline = [stage]
        elif isinstance(stage_conf, str):
            pipeline = [{stage: stage_conf}]
        else:
            raise ValueError()

        pipeline.extend(self.build_route(downstream_pipeline_conf))

        return pipeline

    def build_processor(
        self,
        stage: Processor,
        stage_conf: None,
        downstream_pipeline_conf: List[Union[str, Dict[str, Any]]],
    ) -> List[Union[Stage, Dict[Stage, Any]]]:
        """
        Builds a Processor and its downstream pipeline.

        Args:
            stage: Stage being built
            stage_conf: Configuration of this stage
            downstream_pipeline_conf: Configuration of downstream pipeline

        Returns:
             Pipeline including this stage and those downstream
        """
        pipeline = [stage]
        if stage_conf is not None:
            raise ValueError()

        pipeline.extend(self.build_route(downstream_pipeline_conf))

        return pipeline

    def build_route(
        self, downstream_pipeline_conf: List[Union[str, Dict[str, Any]]]
    ) -> List[Union[Stage, Dict[Stage, Any]]]:
        """
        Builds a downstream pipeline.

        Args:
            downstream_pipeline_conf: Configuration of downstream pipeline

        Returns:
            Downstream pipeline
        """
        if downstream_pipeline_conf is None:
            return []
        if isinstance(downstream_pipeline_conf, str):
            downstream_pipeline_conf = [downstream_pipeline_conf]
        if not isinstance(downstream_pipeline_conf, List):
            raise ValueError()
        elif len(downstream_pipeline_conf) == 0:
            return []

        if isinstance(downstream_pipeline_conf[0], str):
            stage_name, stage_conf = downstream_pipeline_conf.pop(0), None
        elif isinstance(downstream_pipeline_conf[0], dict):
            stage_name, stage_conf = next(iter(downstream_pipeline_conf.pop(0).items()))
        else:
            raise ValueError()

        stage = self.stages[stage_name]
        if isinstance(stage, Merger):
            return self.build_merger(stage, stage_conf, downstream_pipeline_conf)
        elif isinstance(stage, Processor):
            return self.build_processor(stage, stage_conf, downstream_pipeline_conf)
        elif isinstance(stage, Sorter):
            return self.build_sorter(stage, stage_conf, downstream_pipeline_conf)
        elif isinstance(stage, Splitter):
            return self.build_splitter(stage, stage_conf, downstream_pipeline_conf)
        elif isinstance(stage, Terminus):
            return self.build_terminus(stage, stage_conf, downstream_pipeline_conf)
        else:
            raise ValueError()

    def build_sorter(
        self,
        stage: Sorter,
        stage_conf: Optional[Dict[str, Any]],
        downstream_pipeline_conf: List[Union[str, Dict[str, Any]]],
    ) -> List[Union[Stage, Dict[Stage, Any]]]:
        """
        Builds a Sorter and its downstream pipeline.

        Args:
            stage: Stage being built
            stage_conf: Configuration of this stage
            downstream_pipeline_conf: Configuration of downstream pipeline

        Returns:
            Pipeline including this stage and those downstream
        """
        pipeline = [{stage: {}}]
        if isinstance(stage_conf, dict):
            for outlet in filter(lambda o: o in stage_conf, stage.outlets):
                pipeline[0][stage][outlet] = self.build_route(stage_conf.pop(outlet))
            if "default" in stage_conf:
                pipeline[0][stage]["default"] = self.build_route(
                    stage_conf.pop("default")
                )
        elif stage_conf is not None:
            raise ValueError()

        pipeline.extend(self.build_route(downstream_pipeline_conf))

        return pipeline

    def build_source(
        self, stage: Source, downstream_pipeline_conf: List[Union[str, Dict[str, Any]]]
    ) -> List[Union[Stage, Dict[Stage, Any]]]:
        """
        Builds a Source stage and its downstream pipeline.

        Args:
            stage: Stage being built
            downstream_pipeline_conf: Configuration of downstream pipeline

        Returns:
             Pipeline including this stage and those downstream
        """
        pipeline = [stage]
        pipeline.extend(self.build_route(downstream_pipeline_conf))

        return pipeline

    def build_splitter(
        self,
        stage: Splitter,
        stage_conf: Optional[Dict[str, Any]],
        downstream_pipeline_conf: List[Union[str, Dict[str, Any]]],
    ) -> List[Union[Stage, Dict[Stage, Any]]]:
        """
        Builds a Splitter and its downstream pipeline.

        Args:
            stage: Stage being built
            stage_conf: Configuration of this stage
            downstream_pipeline_conf: Configuration of downstream pipeline

        Returns:
             Pipeline including this stage and those downstream
        """
        pipeline = [{stage: {}}]
        if isinstance(stage_conf, dict):
            for outlet in filter(lambda o: o in stage_conf, stage.outlets):
                pipeline[0][stage][outlet] = self.build_route(stage_conf.pop(outlet))
        elif stage_conf is not None:
            raise ValueError()

        pipeline.extend(self.build_route(downstream_pipeline_conf))

        return pipeline

    def build_terminus(
        self, stage: Terminus, stage_conf: None, downstream_pipeline_conf: List[Any],
    ) -> List[Union[Stage, Dict[Stage, Any]]]:
        """
        Builds a Terminus and its downstream pipeline.

        Args:
            stage: Stage being built
            stage_conf: Configuration of this stage
            downstream_pipeline_conf: Configuration of downstream pipeline

        Returns:
             Pipeline including this stage and those downstream
        """
        pipeline = [stage]
        if stage_conf is not None:
            raise ValueError()
        if downstream_pipeline_conf != []:
            raise ValueError()

        return pipeline

    def log_wip_file(self, wip_filename):
        self.wip_files.add(wip_filename)

    def run_route(
        self, downstream_pipeline: List[Union[Stage, Dict[Stage, Any]]], **kwargs: Any
    ):
        if downstream_pipeline is None:
            return kwargs.get("infile", None)
        elif not isinstance(downstream_pipeline, List):
            raise ValueError()
        elif len(downstream_pipeline) == 0:
            return kwargs.get("infile", None)

        if isinstance(downstream_pipeline[0], Stage):
            kwargs["stage"], kwargs["stage_pipeline"] = downstream_pipeline[0], None
        elif isinstance(downstream_pipeline[0], dict):
            kwargs["stage"], kwargs["stage_pipeline"] = next(
                iter(downstream_pipeline[0].items())
            )
        else:
            raise ValueError()

        kwargs["pipeline"] = downstream_pipeline[1:]

        if isinstance(kwargs["stage"], Merger):
            return self.run_merger(**kwargs)
        elif isinstance(kwargs["stage"], Processor):
            return self.run_processor(**kwargs)
        elif isinstance(kwargs["stage"], Sorter):
            return self.run_sorter(**kwargs)
        elif isinstance(kwargs["stage"], Splitter):
            return self.run_splitter(**kwargs)
        elif isinstance(kwargs["stage"], Terminus):
            return self.run_terminus(**kwargs)
        else:
            raise ValueError()

    def run_merger(
        self, stage: Merger, stage_pipeline, image: PipeImage, **kwargs: Any
    ):
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
        self.log_wip_file(outfile)

        return self.run_route(image=image, infile=outfile, **kwargs)

    def run_processor(
        self, stage: Processor, image: PipeImage, infile: str, **kwargs: Any
    ):
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
        self.log_wip_file(outfile)

        return self.run_route(image=image, infile=outfile, **kwargs)

    def run_sorter(
        self, stage: Sorter, stage_pipeline, infile: str, pipeline, **kwargs: Any
    ):
        outlet_name = stage(infile=infile)
        if outlet_name is None and "default" in stage_pipeline:
            outlet_pipeline = stage_pipeline.get("default")
        else:
            outlet_pipeline = stage_pipeline.get(outlet_name, [])

        outfile = self.run_route(
            infile=infile, downstream_pipeline=outlet_pipeline, **kwargs
        )

        return self.run_route(infile=outfile, downstream_pipeline=pipeline, **kwargs)

    def run_splitter(
        self,
        stage: Splitter,
        stage_pipeline,
        image: PipeImage,
        infile: str,
        **kwargs: Any,
    ):
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
            stage(infile=infile, **outfiles)
        for outfile in outfiles.values():
            self.log_wip_file(outfile)

        downstream_inlets = {}
        unsupported_platform_error = None
        for outlet_name in stage.outlets:
            outfile = outfiles[outlet_name]
            outlet_pipeline = stage_pipeline.get(outlet_name, [])
            try:
                outlet_output = self.run_route(
                    downstream_pipeline=outlet_pipeline, image=image, infile=outfile
                )
                if isinstance(outlet_output, dict):
                    downstream_inlets.update(outlet_output)
                # else:
                #     raise ValueError()
            except UnsupportedPlatformError as error:
                warning(
                    f"{self}: While processing '{image.name}', encountered "
                    f"UnsupportedPlatformError '{error}', continuing on to next outlet"
                )
                unsupported_platform_error = error
                continue
        if unsupported_platform_error is not None:
            raise unsupported_platform_error

        kwargs.update(downstream_inlets)
        return self.run_route(image=image, **kwargs)

    def run_terminus(
        self, stage: Terminus, image: PipeImage, infile: str, **kwargs: Any
    ):
        outfile = f"{join(stage.directory, image.name)}{splitext(basename(infile))[1]}"
        stage(infile=infile, outfile=outfile)
        raise TerminusReached(outfile)
