#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Image processing pipeline"""
from __future__ import annotations

from glob import glob
from importlib import import_module
from logging import info, warning
from os import listdir, makedirs, remove, rmdir
from os.path import isdir, isfile, join
from pprint import pformat
from shutil import copyfile
from typing import Any, Optional, Union

from pipescaler.common import UnsupportedPlatformError, validate_output_directory
from pipescaler.core.exception import TerminusReached
from pipescaler.core.merger import Merger
from pipescaler.core.pipe_image import PipeImage
from pipescaler.core.processor import Processor
from pipescaler.core.sorter import Sorter
from pipescaler.core.source import Source
from pipescaler.core.splitter import Splitter
from pipescaler.core.stage import Stage, initialize_stage
from pipescaler.core.terminus import Terminus


class Pipeline:
    """Image processing pipeline"""

    def __init__(
        self,
        wip_directory: str,
        stages: dict[str, dict[str, dict[str, Any]]],
        pipeline: list[Union[str, dict[str, Any]]],
        purge_wip: bool = False,
    ) -> None:
        """
        Validate and store static configuration

        Arguments:
            wip_directory: Directory in which to store intermediate image files
            stages: Stages available to pipeline specification
            pipeline: Pipeline specification
            purge_wip: Purge files in wip_directory that are not intermediates of the
              current pipeline
        """
        # Store configuration
        self.wip_directory = validate_output_directory(wip_directory)
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
        self.stages: dict[str, Stage] = {}
        for stage_name, stage_conf in stages.items():
            self.stages[stage_name] = initialize_stage(
                stage_name, stage_conf, stage_modules
            )

        # Initialize pipeline
        if len(pipeline) == 0:
            raise ValueError("Pipeline must contain at least one stage")
        source_name = pipeline.pop(0)
        if source_name not in self.stages:
            raise KeyError(
                f"Source {source_name} referenced by pipeline does not exist"
            )
        source = self.stages[source_name]
        if not isinstance(source, Source):
            raise ValueError(
                f"First stage in pipeline must be a Source; {source} is not"
            )
        self.pipeline = self.build_source(source, pipeline)
        info(f"{self}: {pformat(self.pipeline)}")

        # Initialize directory
        if not isdir(self.wip_directory):
            info(f"{self}: '{self.wip_directory}' created")
            makedirs(self.wip_directory)
        self.wip_files = set()

    def __call__(self, **kwargs: Any) -> None:
        """Perform operations"""

        source = self.pipeline[0]
        for infile in source:
            info(f"{self}: '{infile}' processing started")
            source_image = PipeImage(infile)

            # Flow into pipeline
            try:
                self.run_route(self.pipeline[1:], source_image)
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
        """Detailed representation of pipeline"""
        return self.__class__.__name__.lower()

    def __str__(self) -> str:
        """Simple representation of image"""
        return self.__class__.__name__.lower()

    def build_merger(
        self,
        stage: Merger,
        stage_conf: Optional[Union[str, dict[str, Any]]],
        downstream_pipeline_conf: list[Union[str, dict[str, Any]]],
    ) -> list[Union[Stage, dict[Stage, Any]]]:
        """
        Build a merger and its downstream pipeline

        Arguments:
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
        stage_conf: Optional[Union[str, dict[str, Any]]],
        downstream_pipeline_conf: list[Union[str, dict[str, Any]]],
    ) -> list[Union[Stage, dict[Stage, Any]]]:
        """
        Build a Processor and its downstream pipeline

        Arguments:
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
        self, pipeline_conf: list[Union[str, dict[str, Any]]]
    ) -> list[Union[Stage, dict[Stage, Any]]]:
        """
        Build a downstream pipeline

        Arguments:
            pipeline_conf: Configuration of pipeline

        Returns:
            Pipeline
        """
        # Organize pipeline configuration
        if pipeline_conf is None:
            return []
        if isinstance(pipeline_conf, str):
            pipeline_conf = [pipeline_conf]
        if not isinstance(pipeline_conf, list):
            raise ValueError()
        if len(pipeline_conf) == 0:
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
        if isinstance(stage, Processor):
            return self.build_processor(stage, stage_conf, pipeline_conf)
        if isinstance(stage, Sorter):
            return self.build_sorter(stage, stage_conf, pipeline_conf)
        if isinstance(stage, Splitter):
            return self.build_splitter(stage, stage_conf, pipeline_conf)
        if isinstance(stage, Terminus):
            return self.build_terminus(stage, stage_conf, pipeline_conf)
        raise ValueError()

    def build_sorter(
        self,
        stage: Sorter,
        stage_conf: Optional[Union[str, dict[str, Any]]],
        downstream_pipeline_conf: list[Union[str, dict[str, Any]]],
    ) -> list[Union[Stage, dict[Stage, Any]]]:
        """
        Build a Sorter and its downstream pipeline

        Arguments:
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
        self, stage: Source, downstream_pipeline_conf: list[Union[str, dict[str, Any]]]
    ) -> list[Union[Stage, dict[Stage, Any]]]:
        """
        Build a Source stage and its downstream pipeline

        Arguments:
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
        stage_conf: Optional[Union[str, dict[str, Any]]],
        downstream_pipeline_conf: list[Union[str, dict[str, Any]]],
    ) -> list[Union[Stage, dict[Stage, Any]]]:
        """
        Build a Splitter and its downstream pipeline

        Arguments:
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
        stage_conf: Optional[Union[str, dict[str, Any]]],
        downstream_pipeline_conf: list[Union[str, dict[str, Any]]],
    ) -> list[Union[Stage, dict[Stage, Any]]]:
        """
        Build a Terminus and its downstream pipeline

        Arguments:
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

    def create_image_wip_directory(self, source_image: PipeImage):
        # Create image working directory
        image_wip_directory = validate_output_directory(
            join(self.wip_directory, source_image.base_filename), create_directory=True
        )

        # Copy initial image to working directory
        initial_image = PipeImage(
            join(image_wip_directory, source_image.full_filename),
            source_image,
        )
        if not isfile(initial_image.absolute_filename):
            copyfile(source_image.absolute_filename, initial_image.absolute_filename)
            info(
                f"{self}: '{source_image.absolute_filename}' "
                f"copied to '{initial_image.absolute_filename}'"
            )
        self.log_wip_file(initial_image.absolute_filename)

        return initial_image

    def log_wip_file(self, wip_filename: str) -> None:
        """
        Mark an intermediate file as having been covered by this pipeline

        Arguments:
            wip_filename: Intermediate file path
        """
        self.wip_files.add(wip_filename)

    def run_merger(
        self,
        stage: Merger,
        stage_pipeline: Optional[Union[Stage, dict[Union[Stage, str], Any]]],
        downstream_pipeline: list[Union[Stage, dict[Stage, Any]]],
        image: Union[PipeImage, dict[str, PipeImage]],
    ):
        """
        Run input images through a Merger and routes output image into downstream
        pipeline

        Arguments:
            stage: Merger to run
            stage_pipeline: Either 1) name of inlet into with input image should flow
              once all inlets are satisfied in upstream splitter, or 2) None, indicating
              that all inlets should be satisfied and Merger is ready to run
            downstream_pipeline: Pipeline downstream from stage
            image: Input images; keys are inlet names and values are images

        Returns:
            Output of downstream pipeline
        """
        if isinstance(stage_pipeline, str):
            return {stage_pipeline: image}

        # Prepare output image
        first_input = next(iter(image.values()))
        if first_input.parent is None:
            raise ValueError("Input images to merge should already have wip directory")
        output = first_input.get_child(
            directory=join(self.wip_directory, first_input.name),
            suffix=stage.suffix,
            trim_suffixes=stage.trim_suffixes,
            extension=stage.extension,
        )

        # Check if output image exists, and if not, run stage
        if not isfile(output.absolute_filename):
            stage(
                outfile=output.absolute_filename,
                **{inlet: input.absolute_filename for inlet, input in image.items()},
            )
        else:
            info(f"{self}: '{output.absolute_filename}' already exists")
        self.log_wip_file(output.absolute_filename)

        # Route merged image to downstream pipeline
        return self.run_route(downstream_pipeline, output)

    def run_processor(
        self,
        stage: Processor,
        stage_pipeline: Optional[Union[Stage, dict[Union[Stage, str], Any]]],
        downstream_pipeline: list[Union[Stage, dict[Stage, Any]]],
        image: Union[PipeImage, dict[str, PipeImage]],
    ):
        """
        Run input image through a Processor and routes output image into
        downstream pipeline

        Arguments:
            stage: Stage to run
            stage_pipeline: Pipeline of this stage
            downstream_pipeline: Pipeline downstream from this stage
            image: Input image

        Returns:
            Output of downstream pipeline
        """
        if stage_pipeline is not None:
            raise ValueError()
        if not isinstance(image, PipeImage):
            raise ValueError()

        # Prepare output image
        if image.parent is None:
            image = self.create_image_wip_directory(image)
        output = image.get_child(
            directory=join(self.wip_directory, image.name),
            suffix=stage.suffix,
            trim_suffixes=stage.trim_suffixes,
            extension=stage.extension,
        )

        # Check if output image exists, and if not, run processor
        if not isfile(output.absolute_filename):
            stage(image.absolute_filename, output.absolute_filename)
        else:
            info(f"{self}: '{output.absolute_filename}' already exists")
        self.log_wip_file(output.absolute_filename)

        # Route output image to downstream pipeline
        return self.run_route(downstream_pipeline, output)

    def run_route(
        self,
        pipeline: list[Union[Stage, dict[Stage, Any]]],
        image: Union[PipeImage, dict[str, PipeImage]],
    ):
        """
        Route image to downstream pipeline

        Arguments:
            pipeline: Pipeline to route to
            image: Input image(s)

        Returns:
            Output of downstream pipeline
        """
        if pipeline is None or (isinstance(pipeline, list) and len(pipeline) == 0):
            return image
        if not isinstance(pipeline, list):
            raise ValueError()

        # Identify stage and stage-specific configuration from pipeline conf
        if isinstance(pipeline[0], Stage):
            stage, stage_pipeline = pipeline[0], None
        elif isinstance(pipeline[0], dict):
            stage, stage_pipeline = next(iter(pipeline[0].items()))
        else:
            raise ValueError()

        if isinstance(stage, Merger):
            return self.run_merger(stage, stage_pipeline, pipeline[1:], image)
        if isinstance(stage, Processor):
            return self.run_processor(stage, stage_pipeline, pipeline[1:], image)
        if isinstance(stage, Sorter):
            return self.run_sorter(stage, stage_pipeline, pipeline[1:], image)
        if isinstance(stage, Splitter):
            return self.run_splitter(stage, stage_pipeline, pipeline[1:], image)
        if isinstance(stage, Terminus):
            return self.run_terminus(stage, stage_pipeline, pipeline[1:], image)
        raise ValueError()

    def run_sorter(
        self,
        stage: Sorter,
        stage_pipeline: Optional[Union[Stage, dict[Union[Stage, str], Any]]],
        downstream_pipeline: list[Union[Stage, dict[Stage, Any]]],
        image: Union[PipeImage, dict[str, PipeImage]],
    ):
        """
        Run input image through an outlet pipeline selected by a Sorter, then
        run output image of that outlet pipeline through a further downstream
        pipeline

        Arguments:
            stage: Stage to run
            stage_pipeline: Pipeline of stage
            downstream_pipeline: Pipeline downstream from stage
            image: Input image

        Returns:
            Output of downstream pipeline
        """
        if not isinstance(image, PipeImage):
            raise ValueError()

        # Determine into which outlet input_image should flow
        outlet = stage(infile=image.absolute_filename)
        if outlet is None and "default" in stage_pipeline:
            outlet_pipeline = stage_pipeline.get("default")
        else:
            outlet_pipeline = stage_pipeline.get(outlet, [])

        # Route image into appropriate outlet
        output = self.run_route(outlet_pipeline, image)

        # Route output of outlet to downstream pipeline
        return self.run_route(downstream_pipeline, output)

    def run_splitter(
        self,
        stage: Splitter,
        stage_pipeline: Optional[Union[Stage, dict[Union[Stage, str], Any]]],
        downstream_pipeline: list[Union[Stage, dict[Stage, Any]]],
        image: Union[PipeImage, dict[str, PipeImage]],
    ):
        """
        Run an input image through a Splitter, and each output image through
        the Splitter's associated outlet pipeline. Collects the outputs of each
        outlet pipeline, and route all of them into downstream pipeline

        Arguments:
            stage: Splitter to run
            stage_pipeline: Pipelines of this Splitter
            downstream_pipeline: Pipeline downstream from this splitter
            image: Input image

        Returns:
            Output of downstream pipeline
        """
        if not isinstance(image, PipeImage):
            raise ValueError()

        # Prepare output images
        if image.parent is None:
            image = self.create_image_wip_directory(image)
        outputs = {
            outlet: image.get_child(
                directory=join(self.wip_directory, image.name),
                suffix=stage.suffixes[outlet],
                trim_suffixes=stage.trim_suffixes,
                extension=stage.extension,
            )
            for outlet in stage.outlets
        }

        # Check if all output images, and if not, run splitter
        to_run = False
        for output in outputs.values():
            if not isfile(output.absolute_filename):
                to_run = True
            else:
                info(f"{self}: '{output.absolute_filename}' already exists")
        if to_run:
            stage(
                infile=image.absolute_filename,
                **{
                    outlet: output.absolute_filename
                    for outlet, output in outputs.items()
                },
            )
        for output in outputs.values():
            self.log_wip_file(output.absolute_filename)

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
        stage_pipeline: Optional[Union[Stage, dict[Union[Stage, str], Any]]],
        downstream_pipeline: list[Union[Stage, dict[Stage, Any]]],
        image: Union[PipeImage, dict[str, PipeImage]],
    ) -> None:
        """
        Run input image through a Terminus

        Arguments:
            stage: Stage to run
            stage_pipeline: Pipeline of this stage
            downstream_pipeline: Pipeline downstream from this stage
            image: Input image

        Raises:
            TerminusReached: Terminus has been run successfully
        """
        if stage_pipeline is not None:
            raise ValueError()
        if downstream_pipeline != []:
            raise ValueError()
        if not isinstance(image, PipeImage):
            raise ValueError()

        outfile = f"{join(stage.directory, image.name)}.{image.extension}"
        stage(image.absolute_filename, outfile)
        raise TerminusReached(outfile)
