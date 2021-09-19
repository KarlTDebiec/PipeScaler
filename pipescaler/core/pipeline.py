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
from importlib.util import module_from_spec, spec_from_file_location
from logging import info, warning
from os import listdir, makedirs, remove, rmdir
from os.path import basename, isdir, isfile, join
from pprint import pformat
from shutil import copyfile
from typing import Any, Dict, List, Optional, Union

from pipescaler.common import validate_input_path, validate_output_path
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

            # Get stage's configuration
            stage_args = stage_conf.get(stage_cls_name)
            if stage_args is None:
                stage_args = {}

            # Get stage's class
            stage_cls = None
            for module in stage_modules:
                try:
                    stage_cls = getattr(module, stage_cls_name)
                except AttributeError:
                    continue
            if stage_cls is None:
                if "infile" in stage_args:
                    module_infile = validate_input_path(stage_args.pop("infile"))
                    spec = spec_from_file_location(stage_cls_name, module_infile)
                    module = module_from_spec(spec)
                    spec.loader.exec_module(module)
                    stage_cls = getattr(module, stage_cls_name)
                else:
                    raise KeyError(f"Class '{stage_cls_name}' not found")

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
            source_image = PipeImage(infile)

            # Create image working directory
            image_directory = validate_output_path(
                join(self.wip_directory, source_image.name),
                file_ok=False,
                directory_ok=True,
                create_directory=True,
            )

            # Backup original image to working directory
            # TODO: Should be handled within source, to support archive sources
            image_backup = PipeImage(
                join(image_directory, basename(source_image.full_path)), source_image
            )
            if not isfile(image_backup.full_path):
                copyfile(source_image.full_path, image_backup.full_path)
                info(
                    f"{self}: '{source_image.full_path}' "
                    f"copied to '{image_backup.full_path}'"
                )
            self.log_wip_file(image_backup.full_path)

            # Flow into pipeline
            try:
                self.run_route(self.pipeline[1:], image_backup)
            except TerminusReached:
                continue
            except UnsupportedPlatformError as error:
                warning(
                    f"{self}: While processing '{source_image.name}', encountered "
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
        stage_conf: Optional[Union[str, Dict[str, Any]]],
        downstream_pipeline_conf: List[Union[str, Dict[str, Any]]],
    ) -> List[Union[Stage, Dict[Stage, Any]]]:
        """
        Builds a merger and its downstream pipeline.

        Args:
            stage: Stage being built
            stage_conf: Configuration of this stage
            downstream_pipeline_conf: Configuration of pipeline downstream from stage

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
        stage_conf: Optional[Union[str, Dict[str, Any]]],
        downstream_pipeline_conf: List[Union[str, Dict[str, Any]]],
    ) -> List[Union[Stage, Dict[Stage, Any]]]:
        """
        Builds a Processor and its downstream pipeline.

        Args:
            stage: Stage being built
            stage_conf: Configuration of this stage
            downstream_pipeline_conf: Configuration of pipeline downstream from stage

        Returns:
             Pipeline including this stage and those downstream
        """
        pipeline = [stage]
        if stage_conf is not None:
            raise ValueError()

        pipeline.extend(self.build_route(downstream_pipeline_conf))

        return pipeline

    def build_route(
        self, pipeline_conf: List[Union[str, Dict[str, Any]]]
    ) -> List[Union[Stage, Dict[Stage, Any]]]:
        """
        Builds a downstream pipeline.

        Args:
            pipeline_conf: Configuration of pipeline

        Returns:
            Pipeline
        """
        # Organize pipeline configuration
        if pipeline_conf is None:
            return []
        if isinstance(pipeline_conf, str):
            pipeline_conf = [pipeline_conf]
        if not isinstance(pipeline_conf, List):
            raise ValueError()
        elif len(pipeline_conf) == 0:
            return []

        # Identify stage and stage-specific configuration from pipeline conf
        if isinstance(pipeline_conf[0], str):
            stage_name, stage_conf = pipeline_conf.pop(0), None
        elif isinstance(pipeline_conf[0], dict):
            stage_name, stage_conf = next(iter(pipeline_conf.pop(0).items()))
        else:
            raise ValueError()

        # Build stage, providing it stage and downstream pipeline configuration
        stage = self.stages[stage_name]
        if isinstance(stage, Merger):
            return self.build_merger(stage, stage_conf, pipeline_conf)
        elif isinstance(stage, Processor):
            return self.build_processor(stage, stage_conf, pipeline_conf)
        elif isinstance(stage, Sorter):
            return self.build_sorter(stage, stage_conf, pipeline_conf)
        elif isinstance(stage, Splitter):
            return self.build_splitter(stage, stage_conf, pipeline_conf)
        elif isinstance(stage, Terminus):
            return self.build_terminus(stage, stage_conf, pipeline_conf)
        else:
            raise ValueError()

    def build_sorter(
        self,
        stage: Sorter,
        stage_conf: Optional[Union[str, Dict[str, Any]]],
        downstream_pipeline_conf: List[Union[str, Dict[str, Any]]],
    ) -> List[Union[Stage, Dict[Stage, Any]]]:
        """
        Builds a Sorter and its downstream pipeline.

        Args:
            stage: Stage being built
            stage_conf: Configuration of this stage
            downstream_pipeline_conf: Configuration of pipeline downstream from stage

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
            downstream_pipeline_conf: Configuration of pipeline downstream from stage

        Returns:
             Pipeline including this stage and those downstream
        """
        pipeline = [stage]
        pipeline.extend(self.build_route(downstream_pipeline_conf))

        return pipeline

    def build_splitter(
        self,
        stage: Splitter,
        stage_conf: Optional[Union[str, Dict[str, Any]]],
        downstream_pipeline_conf: List[Union[str, Dict[str, Any]]],
    ) -> List[Union[Stage, Dict[Stage, Any]]]:
        """
        Builds a Splitter and its downstream pipeline.

        Args:
            stage: Stage being built
            stage_conf: Configuration of this stage
            downstream_pipeline_conf: Configuration of pipeline downstream from stage

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
        self,
        stage: Terminus,
        stage_conf: Optional[Union[str, Dict[str, Any]]],
        downstream_pipeline_conf: List[Union[str, Dict[str, Any]]],
    ) -> List[Union[Stage, Dict[Stage, Any]]]:
        """
        Builds a Terminus and its downstream pipeline.

        Args:
            stage: Stage being built
            stage_conf: Configuration of this stage
            downstream_pipeline_conf: Configuration of pipeline downstream from stage

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

    def run_merger(
        self,
        stage: Merger,
        stage_pipeline: Optional[Union[Stage, Dict[Union[Stage, str], Any]]],
        downstream_pipeline: List[Union[Stage, Dict[Stage, Any]]],
        input: Union[PipeImage, Dict[str, PipeImage]],
    ):
        """
        Runs input images through a Merger and routes output image into
        downstream pipeline.

        Args:
            stage: Merger to run
            stage_pipeline: Either 1) name of inlet into with input image should flow
              once all inlets are satisfied in upstream splitter, or 2) None, indicating
              that all inlets should be satisfied and Merger is ready to run
            downstream_pipeline: Pipeline downstream from stage
            input: Input images; keys are inlet names and values are images

        Returns:
            Output of downstream pipeline
        """
        if isinstance(stage_pipeline, str):
            return {stage_pipeline: input}

        # Prepare output image
        first_input = next(iter(input.values()))
        output = first_input.get_child(
            directory=join(self.wip_directory, first_input.name),
            suffix=stage.suffix,
            trim_suffixes=stage.trim_suffixes,
            extension=stage.extension,
        )

        # Check if output image exists, and if not, run stage
        if not isfile(output.full_path):
            stage(
                outfile=output.full_path,
                **{inlet: input.full_path for inlet, input in input.items()},
            )
        else:
            info(f"{self}: '{output.full_path}' already exists")
        self.log_wip_file(output.full_path)

        # Route merged image to downstream pipeline
        return self.run_route(downstream_pipeline, output)

    def run_processor(
        self,
        stage: Processor,
        stage_pipeline: Optional[Union[Stage, Dict[Union[Stage, str], Any]]],
        downstream_pipeline: List[Union[Stage, Dict[Stage, Any]]],
        input: Union[PipeImage, Dict[str, PipeImage]],
    ):
        """
        Runs input image through a Processor and routes output image into
        downstream pipeline.

        Args:
            stage: Stage to run
            stage_pipeline: Pipeline of this stage
            downstream_pipeline: Pipeline downstream from this stage
            input: Input image

        Returns:
            Output of downstream pipeline
        """
        if stage_pipeline is not None:
            raise ValueError()
        if not isinstance(input, PipeImage):
            raise ValueError()

        # Prepare output image
        output = input.get_child(
            directory=join(self.wip_directory, input.name),
            suffix=stage.suffix,
            trim_suffixes=stage.trim_suffixes,
            extension=stage.extension,
        )

        # Check if output image exists, and if not, run processor
        if not isfile(output.full_path):
            stage(input.full_path, output.full_path)
        else:
            info(f"{self}: '{output.full_path}' already exists")
        self.log_wip_file(output.full_path)

        # Route output image to downstream pipeline
        return self.run_route(downstream_pipeline, output)

    def run_route(
        self,
        pipeline: List[Union[Stage, Dict[Stage, Any]]],
        input: Union[PipeImage, Dict[str, PipeImage]],
    ):
        """
        Routes input to downstream pipeline.

        Args:
            pipeline: Pipeline to route to
            input: Input image(s)

        Returns:
            Output of downstream pipeline
        """
        if pipeline is None or (isinstance(pipeline, list) and len(pipeline) == 0):
            return input
        elif not isinstance(pipeline, list):
            raise ValueError()

        # Identify stage and stage-specific configuration from pipeline conf
        if isinstance(pipeline[0], Stage):
            stage, stage_pipeline = pipeline[0], None
        elif isinstance(pipeline[0], dict):
            stage, stage_pipeline = next(iter(pipeline[0].items()))
        else:
            raise ValueError()

        if isinstance(stage, Merger):
            return self.run_merger(stage, stage_pipeline, pipeline[1:], input)
        elif isinstance(stage, Processor):
            return self.run_processor(stage, stage_pipeline, pipeline[1:], input)
        elif isinstance(stage, Sorter):
            return self.run_sorter(stage, stage_pipeline, pipeline[1:], input)
        elif isinstance(stage, Splitter):
            return self.run_splitter(stage, stage_pipeline, pipeline[1:], input)
        elif isinstance(stage, Terminus):
            return self.run_terminus(stage, stage_pipeline, pipeline[1:], input)
        else:
            raise ValueError()

    def run_sorter(
        self,
        stage: Sorter,
        stage_pipeline: Optional[Union[Stage, Dict[Union[Stage, str], Any]]],
        downstream_pipeline: List[Union[Stage, Dict[Stage, Any]]],
        input: Union[PipeImage, Dict[str, PipeImage]],
    ):
        """
        Runs input image through an outlet pipeline selected by a Sorter, then
        runs output image of that outlet pipeline through a further downstream
        pipeline.

        Args:
            stage: Stage to run
            stage_pipeline: Pipeline of stage
            downstream_pipeline: Pipeline downstream from stage
            input: Input image

        Returns:
            Output of downstream pipeline
        """
        if not isinstance(input, PipeImage):
            raise ValueError()

        # Determine into which outlet input_image should flow
        outlet = stage(infile=input.full_path)
        if outlet is None and "default" in stage_pipeline:
            outlet_pipeline = stage_pipeline.get("default")
        else:
            outlet_pipeline = stage_pipeline.get(outlet, [])

        # Route image into appropriate outlet
        output = self.run_route(outlet_pipeline, input)

        # Route output of outlet to downstream pipeline
        return self.run_route(downstream_pipeline, output)

    def run_splitter(
        self,
        stage: Splitter,
        stage_pipeline: Optional[Union[Stage, Dict[Union[Stage, str], Any]]],
        downstream_pipeline: List[Union[Stage, Dict[Stage, Any]]],
        input: Union[PipeImage, Dict[str, PipeImage]],
    ):
        """
        Runs an input image through a Splitter, and each output image through
        the Splitter's associated outlet pipeline. Collects the outputs of each
        outlet pipeline, and routes all of them into downstream pipeline.

        Args:
            stage: Splitter to run
            stage_pipeline: Pipelines of this Splitter
            downstream_pipeline: Pipeline downstream from this splitter
            input: Input image

        Returns:
            Output of downstream pipeline
        """
        if not isinstance(input, PipeImage):
            raise ValueError()

        # Prepare output images
        outputs = {
            outlet: input.get_child(
                directory=join(self.wip_directory, input.name),
                suffix=stage.suffixes[outlet],
                trim_suffixes=stage.trim_suffixes,
                extension=stage.extension,
            )
            for outlet in stage.outlets
        }

        # Check if all output images, and if not, run splitter
        to_run = False
        for output in outputs.values():
            if not isfile(output.full_path):
                to_run = True
            else:
                info(f"{self}: '{output.full_path}' already exists")
        if to_run:
            stage(
                infile=input.full_path,
                **{outlet: output.full_path for outlet, output in outputs.items()},
            )
        for output in outputs.values():
            self.log_wip_file(output.full_path)

        # Route each output image through its downstream pipeline
        downstream_input = {}
        unsupported_platform_error = None
        for outlet in stage.outlets:
            outlet_input = outputs[outlet]
            outlet_pipeline = stage_pipeline.get(outlet, [])
            try:
                outlet_output = self.run_route(outlet_pipeline, outlet_input)
                if isinstance(outlet_output, dict):
                    downstream_input.update(outlet_output)
                else:
                    raise ValueError()
            except UnsupportedPlatformError as error:
                warning(
                    f"{self}: While processing '{outlet_input.name}', "
                    f"encountered  UnsupportedPlatformError '{error}', continuing on "
                    f"to next outlet before raising"
                )
                unsupported_platform_error = error
                continue
        if unsupported_platform_error is not None:
            raise unsupported_platform_error

        # Route output images to downstream pipeline
        return self.run_route(downstream_pipeline, downstream_input)

    def run_terminus(
        self,
        stage: Terminus,
        stage_pipeline: Optional[Union[Stage, Dict[Union[Stage, str], Any]]],
        downstream_pipeline: List[Union[Stage, Dict[Stage, Any]]],
        input: Union[PipeImage, Dict[str, PipeImage]],
    ) -> None:
        """
        Runs input image through a Terminus.

        Args:
            stage: Stage to run
            stage_pipeline: Pipeline of this stage
            downstream_pipeline: Pipeline downstream from this stage
            input: Input image

        Raises:
            TerminusReached: Terminus has been run successfully
        """
        if stage_pipeline is not None:
            raise ValueError()
        if downstream_pipeline != []:
            raise ValueError()
        if not isinstance(input, PipeImage):
            raise ValueError()

        outfile = f"{join(stage.directory, input.name)}.{input.extension}"
        stage(input.full_path, outfile)
        raise TerminusReached(outfile)
